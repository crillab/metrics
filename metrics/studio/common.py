import os

from jinja2 import Environment, PackageLoader, select_autoescape


class TemplateBuilder:
    def __init__(self, root_dir=os.getcwd()):
        self._root_dir = root_dir
        self._template_vars = {}
        self._env = Environment(loader=PackageLoader('metrics'), autoescape=select_autoescape())

    def get_template_vars(self):
        """
        Returns the template variables.
        """
        return self._template_vars

    def _write_template(self, template_name: str, output_file: str) -> None:
        """
        Writes a campaign file following a template.

        :param template_name: The name of the file to use as template.
        :param output_file: The path of the output file (relative to the root directory of
                            the campaign).
        """
        with open(os.path.join(self._root_dir, output_file), 'w') as file:
            template = self._env.get_template(template_name)
            print(template.render(**self._template_vars), file=file)
