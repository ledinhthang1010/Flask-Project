from flask import Flask, render_template, request,url_for, flash,session,redirect
from flask_mysqldb import MySQL
from flask_login import current_user,LoginManager,UserMixin,login_required,login_user
# LoginManager:dùng để quản lý những thông tin liên quan đến người dùng
# UserMixin: kế thừa các thuộc tính và phương thức
# login_required: ràng buộc đăng nhập
# login_user:kiểm tra thông tin đăng nhập

app = Flask(__name__)
app.secret_key='many random'


# kết nối csdl bằng xamp
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
# Do mật khẩu của xamp mình là rỗng
app.config['MYSQL_PASSWORD']=''
# Tên database trong xamp
app.config['MYSQL_DB']='plan'

# Tạo đối tượng để kết nối với Mysql
mysql=MySQL(app)
# tạo đối tượng LoginManager vào trong app để hỗ trợ cho việc login
login_manager = LoginManager(app)
# Phải đăng nhập trước khi vào trang web
login_manager.login_view = 'login'

# Lớp này dùng để kế thừa các thuộc tính của bảng Users
class User(UserMixin):
    def __init__(self, id_user, username):
        self.id_user = id_user
        self.username = username

    def get_id(self):
        return str(self.id_user)

@login_manager.user_loader
def load_user(id_user):
    # Hàm này được sử dụng bởi Flask-Login để lấy thông tin người dùng từ ID
    # Kết nối với mysql
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id_user = %s", (id_user,))
    # Lấy một dòng sau khi truy vấn
    user_data = cur.fetchone()
    cur.close()

    if user_data:
        return User(id_user=user_data[0], username=user_data[1])
    return None


# route này là dẫn tới trang chủ
@app.route('/')
@login_required 
def hienthi():
    
    # kiểm tra người dùng đã đăng nhập hay chưa
    if current_user.is_authenticated:
        #lấy cái id của người dùng vừa đăng nhập
        user_id = current_user.id_user
        cur = mysql.connection.cursor()
        cur.execute("SELECT id,ngay,noidung,thoigianbatdau,thoigianketthuc,diachi FROM kehoach WHERE id_user=%s", (user_id,))
        data = cur.fetchall()
        cur.close()
        # nó sẽ trả về đường dẫn test.html
        return render_template('test.html',kehoach=data)
    # Nếu không thì nó sẽ trả và lại trang login để yêu cầu đăng nhập 
    return render_template('login.html')


# tạo đường dẫn insert vớI phương thức là Post
@app.route('/insert', methods = ['POST'])
def insert():
    # Kiểm tra nếu nó là Post thì nó sẽ lấy giá trị của các trường mình nhập để insert vào bảng kehoach
    if request.method == "POST":
        # lấy giá trị
        Ngay = request.form['ngay']
         # lấy giá trị
        Noidung = request.form['noidung']
         # lấy giá trị
        Thoigianbatdau = request.form['time_batdau']
         # lấy giá trị
        Thoigianketthuc = request.form['time_ketthuc']
         # lấy giá trị
        DiaChi = request.form['diadiem']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO kehoach (ngay, noidung, thoigianbatdau, thoigianketthuc, diachi,id_user) VALUES (%s, %s, %s, %s, %s, %s)", (Ngay, Noidung, Thoigianbatdau,Thoigianketthuc,DiaChi,current_user.id_user))
        mysql.connection.commit()
        flash("Thêm thành công dữ liệu")
        return redirect(url_for('hienthi'))
# Xoá theo Id thôi
# đường dẫn để nữa đem qua bên test.html nếu như bên test.html không gọi đường dẫn này thì nó hàm này không có tác dụng
@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Xoá thành công")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM kehoach WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('hienthi'))


# Sửa
# đường dẫn để nữa đem qua bên test.html nếu như bên test.html không gọi đường dẫn này thì nó hàm này không có tác dụng
@app.route('/update', methods= ['POST'])
def update():
    # tương tự như insert trên là lấy giá trị
    if request.method == 'POST':
        Iddata = request.form['id']
        Ngay = request.form['ngay']
        Noidung = request.form['noidung']
        Thoigianbatdau = request.form['time_batdau']
        Thoigianketthuc = request.form['time_ketthuc']
        DiaChi = request.form['diadiem']
        
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE kehoach SET ngay=%s, noidung=%s, thoigianbatdau=%s, thoigianketthuc=%s,diachi=%s
        WHERE id=%s
        """, (Ngay, Noidung, Thoigianbatdau, Thoigianketthuc,DiaChi,Iddata))
        # mysql.connection.commit() dòng này dùng để lưu thay đổi khi tiến hành cập nhật, thêm,xoá...
        mysql.connection.commit()
        flash("Cập nhật dữ liệu thành công!")
        return redirect(url_for('hienthi'))
    
    
# ----------------------Login--------------------------

# login
# đường dẫn để nữa đem qua bên test.html nếu như bên test.html không gọi đường dẫn này thì nó hàm này không có tác dụng
@app.route('/login', methods=['GET', 'POST'])
def login():
    # lấy giá trị 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
# nếu như tồn tại một dòng từ kết quả truy vấn trên thì nó sẽ đăng nhập thành công
        if user:
            user_data = User(id_user=user[0], username=user[1])
            login_user(user_data)
            flash('Đăng nhập thành công')
            # trả về hàm hienthi tức là trả về trang test.html
            return redirect(url_for('hienthi'))
        else:
            flash('Đăng nhập không thành công')
            return redirect(url_for('login'))
        

    return render_template('login.html')

# đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
# kiểm tra cả 2 trường mật khẩu trùng nhau
        if password != confirm_password:
           flash('Mật khẩu không trùng khớp', 'error')
           return redirect(url_for('register'))
       
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
# kiểm tra trường user name đã tồn tại hãy chưa nếu tạo lại mà trùng thì..
        if existing_user:
            flash('Tên tài khoản đã tồn tại', 'error')
            return redirect(url_for('register'))
       
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        return redirect(url_for('login'))
        
    return render_template('dangky.html')


# Đăng xuất
@app.route('/dangxuat')
def dangxuat():
    session.clear()
    # Redirect người dùng trở lại trang đăng nhập
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)