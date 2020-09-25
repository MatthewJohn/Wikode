
from flask import render_template, redirect, request


class Admin(object):

    URL = '/admin'

    @staticmethod
    def admin_get():
        return render_template('admin.html')

    @staticmethod
    def admin_post():
        return redirect(Admin.URL)
