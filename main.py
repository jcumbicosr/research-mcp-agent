from research_mcp_agent.cli import main
import sys

if __name__ == "__main__":
    # For quick testing without arguments
    if len(sys.argv) == 1:
        sys.argv.extend(['run', '--file_path', 'samples/input_article_1.txt'])

    main()