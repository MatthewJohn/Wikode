
from flask import render_template, redirect, request


class Admin(object):

    URL = '/admin'

    @staticmethod
    def serve_page():
        if request.method == 'POST':
            return Admin.page_post()
        return render_template('admin.html')

    @staticmethod
    def page_post():
        return redirect(Admin.URL)
