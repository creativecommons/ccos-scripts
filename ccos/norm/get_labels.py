# Standard library
import logging
from pathlib import Path

# Third-party
import yaml

# First-party/Local
from ccos.norm.models import Group, Label

LOG = logging.root


def get_required_label_groups():
    """
    Get the list of all the label_groups, at least one label of which is
    required to be present on every triaged issue.
    @return: the filtered list of label groups that that are required by
        definition
    """
    labels_dict = load_yaml_from_file("labels")
    label_groups = []
    for group_info in labels_dict["groups"]:
        group = Group(**group_info)
        label_names = group_info.pop("labels", [])
        label_groups.append(group)
        for label_info in label_names:
            Label(**label_info, group=group)

    LOG.info(f"Filtering {len(label_groups)} label_groups...")
    required_label_groups = [
        group for group in label_groups if group.is_required
    ]
    LOG.success(f"done. Required {len(required_label_groups)} label groups.")
    return required_label_groups


def get_standard_labels():
    """
    Get the list of standard labels that apply to every repository.
    @return: the list of standard labels
    """
    labels_dict = load_yaml_from_file("labels")
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
    labels_dict = load_yaml_from_file("skills")
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
    skill is plugged into the description and the lower-cased version is used
    as the label name.
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


def load_yaml_from_file(file_name):
    """
    Load the YAML file into a Python list or dict. The extension '.yml' is
    appended to the file name and only the current directory is scanned for the
    matching file.
    @param file_name: the name of the file to load
    @return: the contents of the YAML file as a Python object
    """
    file_path = get_datafile_path(file_name)
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data


def get_datafile_path(file_name):
    """
    Get the path to the datafile by searching the current directory for a file
    with the given name and the '.yml' extension.
    @param file_name: the name of the file whose path is required
    @return: the path to the file
    """
    current_file = Path(__file__).resolve()
    data_file = current_file.parent.joinpath(f"{file_name}.yml")
    return data_file


def get_labels():
    """
    Get the list of standard and repository-specific labels.
    @return: the list of standard and repository-specific labels
    """
    standard_labels = get_standard_labels()
    repo_specific_labels = get_repo_specific_labels()
    return standard_labels, repo_specific_labels


__all__ = ["get_labels", "get_required_label_groups"]
