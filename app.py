from flask import Flask, render_template, request, session, redirect, url_for, Response, jsonify
import mysql.connector
from facedata_generate import facedata_generate
from face_recognition import face_recognition
from face_classifier import face_classifier
from printId import print_nic

app = Flask(__name__)

# Database Configuration
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="voters"
)
mycursor = mydb.cursor()

@app.route('/train_classifier/<nbr>')
def train_classifier(nbr):
    return Response(face_classifier(nbr))

@app.route('/')
def home():
    mycursor.execute("SELECT voter_nic, voter_name, voter_added FROM voters")
    data = mycursor.fetchall()
    return render_template('index.html', data=data)

@app.route('/addprsn')
def addprsn():
    mycursor.execute("SELECT IFNULL(MAX(voter_nic) + 1, 101) FROM voters")
    row = mycursor.fetchone()
    nbr = row[0]
    return render_template('addprsn.html', newnbr=int(nbr))

@app.route('/addprsn_submit', methods=['POST'])
def addprsn_submit():
    prsnbr = request.form.get('txtnbr')
    prsname = request.form.get('txtname')
    mycursor.execute("INSERT INTO `voters` (`voter_nic`, `voter_name`) VALUES (%s, %s)", (prsnbr, prsname))
    mydb.commit()
    return redirect(url_for('vfdataset_page', prs=prsnbr))

@app.route('/vfdataset_page/<prs>')
def vfdataset_page(prs):
    return render_template('gendataset.html', prs=prs)

@app.route('/vidfeed_dataset/<nbr>')
def vidfeed_dataset(nbr):
    return Response(facedata_generate(nbr), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_page')
def camera_page():
    return render_template('camera_page.html')

@app.route('/video_feed')
def video_feed():
    return Response(face_recognition(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_authed_user')
def authed_user():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="voters"
    )
    mycursor = mydb.cursor()

    mycursor.execute("SELECT a.auth_id, a.auth_voter, b.voter_name, a.auth_added "
                 "FROM voters_auth a "
                 "LEFT JOIN voters b ON a.auth_voter = b.voter_nic "
                 "WHERE a.auth_date = CURDATE() "
                 "ORDER BY a.auth_added DESC "
                 "LIMIT 1")
    data = mycursor.fetchall()
    
    return jsonify(response=data)


@app.route('/login_history')
def login_history():
    return render_template('login_history.html')


@app.route('/loadData', methods=['GET', 'POST'])
def loadData():
    mycursor.execute("SELECT a.auth_id, a.auth_voter, b.voter_name, DATE_FORMAT(a.auth_added, '%H:%i:%s') "
                     "FROM voters_auth a "
                     "LEFT JOIN voters b ON a.auth_voter = b.voter_nic "
                     "WHERE a.auth_date = CURDATE() "
                     "ORDER BY 1 DESC")
    data = mycursor.fetchall()
    return jsonify(response=data)



@app.route('/metaMask')
def metaMask():
    return render_template('meta_mask.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
