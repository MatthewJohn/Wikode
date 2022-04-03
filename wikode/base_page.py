
from flask import g, render_template

class BasePage(object):

    def render_template(template_path, **kwargs):
        """Render template and pass arguments """
        return render_template(
            template_path,
            warnings=(g.warnings if 'warnings' in g else []),
            errors=(g.errors if 'errors' in g else []),
            **kwargs
        )

    def add_warning(warning):
        """Add warning to page."""
        if 'warnings' not in g:
            g.warnings = []
        g.warnings.append(warning)

    def add_error(error):
        """Add error to page."""
        if 'errors' not in g:
            g.errors = []
        g.errors.append(error)
