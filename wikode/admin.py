
from flask import render_template, redirect, request

from wikode.scm import Factory as SCMFactory


class Admin(object):

    URL = '/admin'

    @staticmethod
    def admin_get():
        return render_template(
            'admin.html',
            scm_is_setup=SCMFactory.get_scm().is_setup(),
            scm_can_setup=SCMFactory.get_scm().can_setup())

    @staticmethod
    def admin_post():
        if request.form.get('action', '') == 'scm_setup':
            SCMFactory.get_scm().setup()
        return redirect(Admin.URL)
