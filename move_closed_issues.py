#!/usr/bin/env python3
"""
Move closed Issues out of Backlog and into Active Sprint: Done.
"""
# Standard library
import os
import sys
import traceback

# Third-party
import github

GITHUB_TOKEN = os.environ["ADMIN_GITHUB_TOKEN"]


class ScriptError(Exception):
    def __init__(self, message, code=None):
        self.code = code if code else 1
        message = "({}) {}".format(self.code, message)
        super(ScriptError, self).__init__(message)


def main():
    backlog = None
    active_sprint = None
    done = None
    github_client = github.Github(GITHUB_TOKEN)
    cc = github_client.get_organization("creativecommons")

    for project in cc.get_projects():
        if project.name == "Active Sprint":
            active_sprint = project
        elif project.name == "Backlog":
            backlog = project

    for column in active_sprint.get_columns():
        if column.name == "Done":
            done = column
            break

    for column in backlog.get_columns():
        print(f"{backlog.name}: {column.name}")
        for card in column.get_cards():
            if not card.content_url or "/issues/" not in card.content_url:
                continue
            content = card.get_content(content_type="Issue")
            if content.state != "closed":
                continue
            print(f"    {content.title}")
            try:
                done.create_card(content_id=content.id, content_type="Issue")
                print(f"     -> added to Active Sprint: {done.name}")
            except github.GithubException as e:
                if e.data["errors"][0]["message"] != (
                    "Project already has the associated issue"
                ):
                    raise
            card.delete()
            print("     -> removed.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
    except KeyboardInterrupt:
        print("INFO (130) Halted via KeyboardInterrupt.", file=sys.stderr)
        sys.exit(130)
    except ScriptError:
        error_type, error_value, error_traceback = sys.exc_info()
        print("ERROR {}".format(error_value), file=sys.stderr)
        sys.exit(error_value.code)
    except Exception:
        print("ERROR (1) Unhandled exception:", file=sys.stderr)
        print(traceback.print_exc(), file=sys.stderr)
        sys.exit(1)
