from flask import render_template, redirect, url_for
from flask import flash, request
from flask_login import login_user, current_user, logout_user, login_required
from myapp import app, db, ipfs_utils
from myapp.forms import LoginForm, UploadTranscriptForm
from myapp.models import User, Transcript


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Login failed. Check email and password.", "danger")

    return render_template("index.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if current_user.is_admin:
        form = UploadTranscriptForm()
        if form.validate_on_submit():
            student = User.query.filter_by(email=form.student_email.data).first()
            if student:
                file = request.files[form.transcript_file.name]
                ipfs_hash = ipfs_utils.add_file_to_ipfs(file)
                transcript = Transcript(student_id=student.id, ipfs_hash=ipfs_hash)
                db.session.add(transcript)
                db.session.commit()
                flash("Transcript uploaded successfully.", "success")
            else:
                flash("Student not found.", "danger")
        return render_template("admin_upload.html", form=form)
    else:
        transcripts = current_user.transcripts
        return render_template("student_view.html", transcripts=transcripts)


if __name__ == "__main__":
    app.run()
