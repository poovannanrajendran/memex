import os
import pytest
from unittest.mock import MagicMock, patch
from scripts.lint import check_staleness, run_lint

def test_check_staleness_disabled_by_default(tmp_path):
    # Create mock wiki structure
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    page = wiki_dir / "test_page.md"
    page.write_text(
        "---\n"
        "title: Test Stale Page\n"
        "ingested: 2024-01-01\n"
        "---\n\n"
        "Some historical claims."
    )
    
    with patch("os.walk") as mock_walk, \
         patch("scripts.lint.check_staleness") as mock_check:
        mock_walk.return_value = [
            (str(wiki_dir), [], ["test_page.md"])
        ]
        
        # Run lint without grounding (default)
        run_lint(run_id="test_run", enable_grounding=False)
        
        # Ensure search grounding was NOT called
        mock_check.assert_not_called()

def test_check_staleness_capped_when_enabled(tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    
    stale_files = []
    for i in range(10):
        f = wiki_dir / f"page_{i}.md"
        f.write_text(
            f"---\ntitle: Stale Page {i}\ningested: 2024-01-01\n---\nContent"
        )
        stale_files.append(f"page_{i}.md")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Still accurate"
    mock_response.usage_metadata.prompt_token_count = 100
    mock_response.usage_metadata.candidates_token_count = 50
    mock_client.models.generate_content.return_value = mock_response

    with patch("os.walk") as mock_walk, \
         patch("google.genai.Client", return_value=mock_client), \
         patch.dict("os.environ", {"GEMINI_API_KEY": "dummy_key"}):
        mock_walk.return_value = [
            (str(wiki_dir), [], stale_files)
        ]
        
        # Test capping at 3 checks
        with patch("scripts.lint.check_staleness", wraps=check_staleness) as spy_check:
            run_lint(run_id="test_run", enable_grounding=True, max_grounding_checks=3)
            assert spy_check.call_count == 3
