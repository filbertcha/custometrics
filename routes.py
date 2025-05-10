from flask import render_template, redirect, url_for, flash, send_file, request
from flask_login import login_user, logout_user, login_required, current_user

from __init__ import app, User, db, DataScraping
from forms import RegisterForm, LoginForm, LinkForm
from scraping import scrape_website, preprocess_text
import pandas as pd
import io

@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')

@app.route("/pengumpulanlink", methods=['GET', 'POST'])
@login_required
def pengisian_link_page():
    form = LinkForm()
    if request.method == 'POST' and form.validate_on_submit():
        link_url = form.link.data
        
        # Panggil fungsi scraping untuk mendapatkan data
        prompt, response = scrape_website(link_url)
        
        # Preprocessing data
        prompt_preprocessed = preprocess_text(prompt)
        response_preprocessed = preprocess_text(response)
        
        # Buat objek data scraping dan simpan ke database
        # Pastikan data terhubung dengan user yang sedang login
        data_scraping = DataScraping(
            link=link_url,
            prompt=prompt,
            response=response,
            prompt_preprocessing=prompt_preprocessed,
            response_preprocessing=response_preprocessed,
            owner_id=current_user.id,
            owner_username=current_user.username  # Tambahkan username pemilik
        )
        
        db.session.add(data_scraping)
        db.session.commit()
        
        flash(f'Data berhasil disimpan untuk pengguna {current_user.username}!', category='success')
        return redirect(url_for('my_data_page'))
    
    if form.errors:
        for err_msg in form.errors.values():
            flash(f'Terjadi kesalahan: {err_msg}', category='danger')
    
    return render_template('formLink.html', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data, 
            email_address=form.email_address.data,
            password=form.password1.data
        )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as {user_to_create.username}', category='success')
        return redirect(url_for('home_page'))
    
    if form.errors:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password do not match! Please try again', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out", category='info')
    return redirect(url_for("home_page"))

@app.route('/mydata')
@login_required
def my_data_page():
    # Ambil data scraping milik user yang sedang login
    user_data = DataScraping.query.filter_by(owner_id=current_user.id).order_by(DataScraping.created_at.desc()).all()
    return render_template('mydata.html', data_list=user_data)

@app.route('/export/csv')
@login_required
def export_csv():
    # Ambil data scraping milik user yang sedang login
    user_data = DataScraping.query.filter_by(owner_id=current_user.id).all()

    # Konversi ke DataFrame
    data = {
        "ID": [data_temp.id for data_temp in user_data],
        "Created At": [data_temp.created_at for data_temp in user_data],
        "Link": [data_temp.link for data_temp in user_data],
        "Prompt": [data_temp.prompt for data_temp in user_data],
        "Response": [data_temp.response for data_temp in user_data],
        "Prompt Preprocessing": [data_temp.prompt_preprocessing for data_temp in user_data],
        "Response Preprocessing": [data_temp.response_preprocessing for data_temp in user_data],
        "Owner ID": [data_temp.owner_id for data_temp in user_data],
        "Owner Username": [data_temp.owner_username for data_temp in user_data],
    }
    df = pd.DataFrame(data)

    # Simpan ke buffer dalam format CSV
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name="data_scrapping.csv"
    )

@app.route('/export/excel')
@login_required
def export_excel():
    # Ambil data scraping milik user yang sedang login
    user_data = DataScraping.query.filter_by(owner_id=current_user.id).all()

    # Konversi ke DataFrame
    data = {
        "ID": [data_temp.id for data_temp in user_data],
        "Created At": [data_temp.created_at for data_temp in user_data],
        "Link": [data_temp.link for data_temp in user_data],
        "Prompt": [data_temp.prompt for data_temp in user_data],
        "Response": [data_temp.response for data_temp in user_data],
        "Prompt Preprocessing": [data_temp.prompt_preprocessing for data_temp in user_data],
        "Response Preprocessing": [data_temp.response_preprocessing for data_temp in user_data],
        "Owner ID": [data_temp.owner_id for data_temp in user_data],
        "Owner Username": [data_temp.owner_username for data_temp in user_data],
    }
    df = pd.DataFrame(data)

    # Simpan ke buffer dalam format Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name="data_scrapping.xlsx"
    )

@app.route('/admin/alldata')
@login_required
def all_data_page():
    # Hanya admin yang bisa melihat semua data
    if current_user.username == "admin":
        all_data = DataScraping.query.order_by(DataScraping.created_at.desc()).all()
        all_users = User.query.all()
        return render_template('admindata.html', data_list=all_data, users=all_users)
    else:
        flash("You are not authorized to view this page!", category='danger')
        return redirect(url_for('home_page'))
    
@app.route('/export/csv_all')
@login_required
def export_csv_all():
    # Hanya admin yang bisa melihat semua data
    if current_user.username == "admin":
        # Ambil data scraping milik user yang sedang login
        user_data = DataScraping.query.all()

        # Konversi ke DataFrame
        data = {
            "ID": [data_temp.id for data_temp in user_data],
            "Created At": [data_temp.created_at for data_temp in user_data],
            "Link": [data_temp.link for data_temp in user_data],
            "Prompt": [data_temp.prompt for data_temp in user_data],
            "Response": [data_temp.response for data_temp in user_data],
            "Prompt Preprocessing": [data_temp.prompt_preprocessing for data_temp in user_data],
            "Response Preprocessing": [data_temp.response_preprocessing for data_temp in user_data],
            "Owner ID": [data_temp.owner_id for data_temp in user_data],
            "Owner Username": [data_temp.owner_username for data_temp in user_data],
        }
        df = pd.DataFrame(data)

        # Simpan ke buffer dalam format CSV
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        return send_file(
            io.BytesIO(buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name="all_data_scrapping.csv"
        )
    else:
        flash("You are not authorized to view this page!", category='danger')
        return redirect(url_for('home_page'))

@app.route('/export/excel_all')
@login_required
def export_excel_all():
    # Hanya admin yang bisa melihat semua data
    if current_user.username == "admin":
        # Ambil data scraping milik user yang sedang login
        user_data = DataScraping.query.all()

        # Konversi ke DataFrame
        data = {
            "ID": [data_temp.id for data_temp in user_data],
            "Created At": [data_temp.created_at for data_temp in user_data],
            "Link": [data_temp.link for data_temp in user_data],
            "Prompt": [data_temp.prompt for data_temp in user_data],
            "Response": [data_temp.response for data_temp in user_data],
            "Prompt Preprocessing": [data_temp.prompt_preprocessing for data_temp in user_data],
            "Response Preprocessing": [data_temp.response_preprocessing for data_temp in user_data],
            "Owner ID": [data_temp.owner_id for data_temp in user_data],
            "Owner Username": [data_temp.owner_username for data_temp in user_data],
        }
        df = pd.DataFrame(data)

        # Simpan ke buffer dalam format Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name="all_data_scrapping.xlsx"
        )
    else:
        flash("You are not authorized to view this page!", category='danger')
        return redirect(url_for('home_page'))
        
@app.route('/data/<int:data_id>')
@login_required
def view_data_detail(data_id):
    data = DataScraping.query.get_or_404(data_id)
    # Pastikan pengguna hanya bisa melihat datanya sendiri (kecuali admin)
    if data.owner_id != current_user.id and current_user.username != "admin":
        flash("You are not authorized to view this data!", category='danger')
        return redirect(url_for('home_page'))
    
    return render_template('data_detail.html', data=data)

@app.route('/data/<int:data_id>/preprocessed')
@login_required
def view_data_detail_preprocessed(data_id):
    data = DataScraping.query.get_or_404(data_id)
    # Pastikan pengguna hanya bisa melihat datanya sendiri (kecuali admin)
    if data.owner_id != current_user.id and current_user.username != "admin":
        flash("You are not authorized to view this data!", category='danger')
        return redirect(url_for('home_page'))
    
    return render_template('data_detail_preprocessing.html', data=data)