COLORS = {
    "UNFAVOURABLE": "b60205",
    "NEGATIVE": "ff9f1c",
    "NEUTRAL": "ffcc00",
    "POSITIVE": "cfda2c",
    "FAVOURABLE": "008672",
    "BLACK": "000000",
    "DARKER": "333333",
    "DARK": "666666",
    "MEDIUM": "999999",
    "LIGHT": "cccccc",
    "LIGHTER": "eeeeee",
    "WHITE": "ffffff",
}


class Group:
    """
    This model represents a group of labels. A group has some fixed parameters
    - name, which may be prefixed to all child label names
    - color, which acts as a fallback for child labels that do not specify one
    - is_prefixed, which determines if group name is prefixed on child labels
    - is_required, which determines if >=1 sub-label must be applied on issues
    """

    def __init__(
        self, color=None, is_prefixed=True, is_required=False, **kwargs
    ):
        self.name = kwargs["name"]
        self.color = color
        self.is_prefixed = is_prefixed
        self.is_required = is_required

        self.labels = []  # This may or may not be populated, do not rely

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Group '{self}'>"


class Label:
    """
    This model represents a single label. A label is defined by four parameters
    - name, which appears on the label
    - description, which describes it in a little more detail
    - emoji, which is a pictorial representation of the purpose of the label
    - color, which is used as a background on the label element

    A ``Label`` instance is associated to a ``Group`` instance by a many to one
    relationship.
    """

    def __init__(self, group=None, color=None, has_emoji_name=True, **kwargs):
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.emoji = kwargs["emoji"]
        self.own_color = color
        self.has_emoji_name = has_emoji_name

        self.group = group
        if group and self not in group.labels:
            group.labels.append(self)

    @property
    def color(self):
        """
        Return the color to use on the emoji label, given as a 6-digit
        hexadecimal code without the prefix '#'. Labels can have their color
        specified as a constant and if missing inherit color from the parent
        group. If not resolved, the color defaults to pure black.
        @return: the 6-digit hexadecimal code of the background color
        """

        color = self.own_color
        if color is None and self.group is not None:
            color = self.group.color
        elif color is None:
            color = COLORS["BLACK"]
        elif color in COLORS:
            color = COLORS[color]
        return color

    @property
    def qualified_name(self):
        """
        Return the fully qualified name of the label. Most label groups prefix
        the group name to the name of the label, separated by a dunder, as
        indicated by the ``is_prefixed`` attribute on the associated ``Group``
        instance.
        @return: the fully qualified name of the label
        """

        name = self.name
        if self.group and self.group.is_prefixed:
            name = f"{self.group}: {name}"
        if self.has_emoji_name:
            name = f"{self.emoji} {name}"
        return name

    @property
    def emojified_description(self):
        """
        TODO: Use this when GitHub supports Unicode in label descriptions

        Get the description of the label prefixed with the emoji.
        @return: the emoji-prefixed description
        """

        return f"{self.emoji} {self.description}"

    @property
    def api_arguments(self):
        """
        Get the dictionary of arguments to pass to the API for creating the
        label. The API only accepts ``name``, ``color`` and ``description``.
        @return: the API arguments as a dictionary
        """

        return {
            "name": self.qualified_name,
            "color": self.color,
            "description": self.description,
        }

    def __eq__(self, remote):
        """
        Compare this instance with the corresponding PyGithub instance to
        determine whether the two are equal.
        @param remote: the PyGithub label instance to compare itself against
        @return: whether the instance is equal to its remote counterpart
        """

        return all(
            [
                self.qualified_name == remote.name,
                self.color == remote.color,
                self.description == remote.description,
            ]
        )

    def __ne__(self, remote):
        """
        Compare this instance with the corresponding PyGithub instance to
        determine whether the two are unequal and would need to be reconciled.
        @param remote: the PyGithub label instance to compare itself against
        @return: whether the instance is unequal to its remote counterpart
        """

        return any(
            [
                self.qualified_name != remote.name,
                self.color != remote.color,
                self.description != remote.description,
            ]
        )

    def __str__(self):
        return self.qualified_name

    def __repr__(self):
        return f"<Label '{self}'>"
