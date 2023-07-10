from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from functools import wraps
from hashlib import sha256
import json, requests


app = Flask(__name__)
app.secret_key = 'asdiquwbebd12365sasdADASDdfn'

# def get_curret_user():
#     if session.get('logged_in'):
#         return User.get(User.id == session['user_id'])

def auth_user(user):
    session['logged_in'] = True
    # session['user_id'] = user.id
    # session['nama'] = ka

def get_curret_user():
    if session.get('logged_in'):
        return session['id_orangtua']
    # session['user_id']

def redirect_to_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('id_orangtua'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def redirect_after_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('id_orangtua'):
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def format_rupiah(number):
    # Mengubah angka menjadi string dan menghapus karakter non-digit
    number = str(number).replace(',', '').replace('.', '')

    # Mengecek apakah angka valid
    if not number.isdigit():
        raise ValueError('Invalid number')

    # Mengubah string angka menjadi integer
    number = int(number)

    # Mengubah angka menjadi format rupiah
    rupiah = "Rp. {:,}".format(number).replace(',', '.')

    return rupiah



@app.route('/', methods=['GET','POST'])
@redirect_after_login
def index():
	if request.method == 'POST':
		form_username = request.form['username']
		form_password = request.form['password']

		data_login = {
	    	"username" : form_username,
	    	"password" : form_password
	    	}
			
		dataLogin_json = json.dumps(data_login)
		alamatserver = "http://localhost:5055/api/loginorangtua"
		headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
		kirimdata = requests.post(alamatserver, data=dataLogin_json, headers=headers)
		cow = json.loads(kirimdata.text)

		# print(cow)
		if cow["message"] == "sukses": 	
			session['username'] = form_username
			session["id_orangtua"] = cow["auth_orangtua"]["orangtua_id"]
			return redirect(url_for('dashboard'))
		elif cow["message"] == "gagal":
			flash('Data orangtua tidak ditemukan', 'alert-danger')
            
	return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@redirect_to_login
def dashboard():
	# if request.method == 'POST':
	# 	error = None
	# 	orangtua_id = session["id_orangtua"]
	# 	# inputSearch = request.form['formoption']
	# 	if not inputSearch or not inputSearch.strip():
	# 		error = 'Pilih nama anak terlebih dahulu'

	# 	if error != None:
	# 		flash(error, 'errors')
	# 		return redirect(url_for('dashboard'))
		
	# 	try :
	# 		if error is None:
	# 			data_search = {
	# 				"formoption" : inputSearch
	# 			}

	# 			dataSearch_json = json.dumps(data_search)
	# 			alamatserver = f"http://localhost:5055/api/searchdatabynama/{orangtua_id}"
	# 			headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
	# 			kirimdata = requests.get(alamatserver, data=dataSearch_json, headers=headers)
	# 			cow = json.loads(kirimdata.text)

	# 			getPesanan = cow["data"]
	# 			getTotalSaldo = cow["totalsaldo"]
	# 			getTotalPembelian = cow["totalpembelian"]

	# 			return redirect(url_for('detaildashboard', getPesanan=getPesanan, getTotalPembelian=getTotalPembelian, getTotalSaldo=getTotalSaldo))
	# 	except:
	# 		flash("ada yang error", 'errors')

	# error = None
	# inputSearch = request.form['formoption']

	# if not inputSearch or not inputSearch.strip():
	# 	error = 'Pilih nama anak terlebih dahulu'

	# if error != None:
	# 	flash(error, 'errors')
	# 	return redirect(url_for('dashboard'))


	# ##################### Resources MENAMPILKAN SEMUA HISTORI PEMBELIAN ANAK ###############
	orangtua_id = session["id_orangtua"]
	# print(orangtua_id)
	alamatserver = f"http://localhost:5055/api/historipesanans/{orangtua_id}"
	# alamatserver = ''
	datas = requests.get(alamatserver)

	rows = json.loads(datas.text)

	# ##################### Resources TOTAL SALDO SEMUA ANAK ###################
	requestTotalSaldo = f"http://localhost:5055/api/totalsaldoanaks/{orangtua_id}"
	getsaldo = requests.get(requestTotalSaldo)

	saldos= json.loads(getsaldo.text)

	totalsaldo = saldos["messages"]
	# print(totalsaldo)

	#  #################### Resources TOTAL PEMBELIAN SELURUH ANAK ###############
	requestTotalPembelian = f"http://localhost:5055/api/totalpembelians/{orangtua_id}"
	getTotalPembelian = requests.get(requestTotalPembelian)
	jumlahPembelian = json.loads(getTotalPembelian.text)
	totalPembelian = jumlahPembelian['messages']


	# ##################### Resource Nama Anak Yang Ada Berdasarkan Id Orang Tua ###########################
	requestNamaAnaks = f"http://localhost:5055/api/namaanaks/{orangtua_id}"
	getNamaAnak = requests.get(requestNamaAnaks)
	namas = json.loads(getNamaAnak.text)


	return render_template(
		'dashboard.html',
		rows=rows,
		totalsaldo=totalsaldo,
		totalPembelian=totalPembelian,
		namas=namas,
		format_rupiah=format_rupiah)

@app.route('/dashboard/search', methods=['GET','POST'])
def detaildashboard():
	error = None
	orangtua_id = session["id_orangtua"]
	inputSearch = request.form['formoption']

	if not inputSearch or not inputSearch.strip():
            error = 'Pilih nama anak terlebih dahulu'

	if error != None:
		 flash(error, 'alert-danger')
		 return redirect(url_for('dashboard'))
	elif error is None:
		data_search = {
			"formoption" : inputSearch
			}
		dataSearch_json = json.dumps(data_search)
		alamatserver = f"http://localhost:5055/api/searchdatabynama/{orangtua_id}"
		headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
		kirimdata = requests.get(alamatserver, data=dataSearch_json, headers=headers)
		cow = json.loads(kirimdata.text)

		getPesanan = cow["data"]
		getTotalSaldo = cow["totalsaldo"]
		getTotalPembelian = cow["totalpembelian"]
		getNama = cow["namanya"]

		return render_template('focusanak.html', getPesanan=getPesanan, getTotalPembelian=getTotalPembelian, getTotalSaldo=getTotalSaldo, format_rupiah=format_rupiah, getNama=getNama)
	

@app.route('/profile')
@redirect_to_login
def profile():
	orangtua_id = session["id_orangtua"]

	alamatserver = f"http://localhost:5055/api/dataorangtua/{orangtua_id}"
	headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
	datas = requests.get(alamatserver, headers=headers)
	rows = json.loads(datas.text)

	return render_template('profile.html', rows=rows)

@app.route('/anak')
@redirect_to_login
def anak():
	orangtua_id = session["id_orangtua"]

	alamatserver = f"http://localhost:5055/api/dataanak/{orangtua_id}"
	headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
	datas = requests.get(alamatserver, headers=headers)
	rows = json.loads(datas.text)

	getData = rows['datas']

	return render_template('anak.html', getData=getData)

@app.route('/detail/<int:id>', methods=['GET', 'POST'])
@redirect_to_login
def detail(id):

	alamatserver = f"http://127.0.0.1:5055/api/detailpesanan/{id}"
	headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
	datas = requests.get(alamatserver, headers=headers)

	rows = json.loads(datas.text)

	detailPesanan = rows['detail']
	namaanak = rows['namanya']
	ttl_pemesanan = rows['ttl_pemesanan']
	totalPembayaran = rows['totalPembayaran']

	totalHarga = format_rupiah(totalPembayaran)
	print(totalHarga)

	return render_template('detail.html', detailPesanan=detailPesanan, namaanak=namaanak, ttl_pemesanan=ttl_pemesanan, totalHarga=totalHarga, format_rupiah=format_rupiah)


@app.route('/logout', methods=['GET','POST'])
def logout():
	if request.method == 'GET':
		# membuat data dummy untuk permintaan menghapus session pada server yang id karyawan
		hapus_session = {
            'session_hapus' : True
        }

		dataHapusSession_json = json.dumps(hapus_session)
		alamatserver = "http://localhost:5055/api/logoutorangtua"
		headers = {'Content-Type':'application/json', 'Accept':'text/plain'}
		kirimdata = requests.get(alamatserver, data=dataHapusSession_json, headers=headers)
        
	session.pop('id_orangtua', None)
	flash('Logout berhasil','alert-success')
	return redirect(url_for('index'))









if __name__ == '__main__':
	app.run(
		debug=True,
		host='0.0.0.0'
		)