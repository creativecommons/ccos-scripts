# Standard library
from pathlib import Path
import json

# Local/library specific
from models import Group, Label


def get_standard_labels():
    """
    Get the list of standard labels that apply to every repository.
    @return: the list of standard labels
    """

    labels_dict = load_json_from_file("labels")
    standard_labels = []
    for group_info in labels_dict["groups"]:
        label_names = group_info.pop("labels", [])
        group = Group(**group_info)
        for label_info in label_names:
            label = Label(**label_info, group=group)
            standard_labels.append(label)
    for label_info in labels_dict["standalone"]:
        label = Label(**label_info)
        standard_labels.append(label)
    return standard_labels


def get_repo_specific_labels():
    """
    Get the dict mapping each repository to a list of skill labels. For each
    repository, skill levels will be added on top of the standard labels.
    @return: the dict mapping repo names to skill labels
    """

    skill_group = Group(color="5ff1f5", name="skill")
    labels_dict = load_json_from_file("skills")
    repo_specific_labels = {}
    for repo_name, skill_names in labels_dict.items():
        skill_labels = [
            get_skill_label_from_name(skill_group, skill_name)
            for skill_name in skill_names
        ]
        repo_specific_labels[repo_name] = skill_labels
    return repo_specific_labels


def get_skill_label_from_name(skill_group, skill_name):
    """
    Generate the skill label purely from the name of the skill. The name of the
    skill is plugged into the description and the lower-cased version is used as
    the label name.
    @param skill_group: the logical parent group of all skill labels
    @param skill_name: the name of the skill to convert into a label
    @return: an instance of Label derived from the skill name
    """

    return Label(
        name=skill_name.lower(),
        description=f"Requires proficiency in '{skill_name}'",
        emoji="💪",
        group=skill_group,
    )


def load_json_from_file(file_name):
    """
    Load the JSON file into a Python list or dict. The extension '.json' is
    appended to the file name and only the current directory is scanned for the
    matching file.
    @param file_name: the name of the file to load
    @return: the contents of the JSON file as a Python object
    """

    file_path = get_datafile_path(file_name)
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def get_datafile_path(file_name):
    """
    Get the path to the datafile by searching the current directory for a file
    with the given name and the '.json' extension.
    @param file_name: the name of the file whose path is required
    @return: the path to the file
    """

    current_file = Path(__file__).resolve()
    data_file = current_file.parent.joinpath(f"{file_name}.json")
    return data_file


def get_labels():
    """
    Get the list of standard and repository-specific labels.
    @return: the list of standard and repository-specific labels
    """

    standard_labels = get_standard_labels()
    repo_specific_labels = get_repo_specific_labels()
    return standard_labels, repo_specific_labels


__all__ = [get_labels]
