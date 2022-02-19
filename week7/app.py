import mysql.connector
from flask import request
from flask import *
import json

db = mysql.connector.connect(user='root',password='1qaz2wsx',host='localhost',database='member_system')
cursor = db.cursor()

# 初始化 Flask 伺服器
app = Flask(__name__,static_folder="public",static_url_path="/")
app.secret_key="any string but secret"

# 更名
def changeUserNamef(newUserName):
    # session有紀錄才能更名，且用session紀錄的name改名
    if "username" in session:
        username=session.get("username")
        # 更新
        cursor.execute("UPDATE member SET username='%s' WHERE username='%s'"% (newUserName,username))
        db.commit()
        # 搜尋的到才代表更改成功
        result=searchUserName(newUserName)
        if result!=[]:
            # 轉成json格式
            data=json.dumps({"OK":result[0][2]==newUserName})
            session["username"]=result[0][2]
            return data

        else:
            data=json.dumps({"error":result==[]})
            return data
    else:
        return "請重新登入"

# 搜尋username
def searchUserName(username):
    sql_search = "SELECT id,name,username,password FROM member WHERE username ='%s'"%(username)
    cursor.execute(sql_search)
    search_Result = cursor.fetchall()
    return search_Result
        
# 首頁
@app.route("/")
def index():
    return render_template("index.html")

# 錯誤頁
@app.route("/error")
def error():
    message=request.args.get("msg","發生錯誤，請聯繫客服")
    return render_template("error.html",message=message)

# 註冊
@app.route("/signup",methods=["POST"])
def signup():
    # 從前端接受資料
    signup_name=request.form["name"]
    signup_username=request.form["username"]
    signup_password=request.form["password"]
    result=searchUserName(signup_username)
    # 輸入的name跟username不是空值的話
    if signup_name!="" and signup_username!="" and signup_password!="":
        # 搜尋註冊的usernam有沒有存在在資料庫裏面
        if result!=None:
            # 沒有註冊過，新增mysql資料庫
            sql_signin = "INSERT INTO member (name, username, password) VALUES (%s, %s, %s)"
            val = (signup_name, signup_username, signup_password)
            cursor.execute(sql_signin,val)
            db.commit()
            return redirect("/")
        return redirect("/error?msg=帳號、密碼已被註冊")
    else:
        return redirect("/error?msg=請輸入要註冊的帳號密碼")

# 登錄
@app.route("/signin",methods=["POST"])
def signin():
    # 從前端取得使用者的輸入
    signin_username=request.form["username"]
    signin_password=request.form["password"]
    result=searchUserName(signin_username)
    if result!=[]:
        # 帳號跟密碼任意一個不對
        if result[0][2]!=signin_username or result[0][3]!=signin_password:
            return redirect("/error?msg=帳號密碼輸入錯誤")
        else:
            # 登入成功，在 Session 記錄會員資訊，導向到會員資料
            session["username"]=result[0][2]
            return redirect("/member")
    else:
        return redirect("/error?msg=請輸入帳號密碼")

# 會員頁
@app.route("/member/")
def member():
    username=session.get("username")
    if "username" in session:
        # 使用者名稱顯示在member頁面name=name及頁面設定{{ username }}
        return render_template("member.html",username=username)

    else:
        return redirect("/")

# api查詢姓名
@app.route("/api/members")
def apiSearchMembers():
    # 從api來的查詢request
    api_search_Uename=request.args.get("username")    # 搜尋使用名稱是否在資料庫中
    result=searchUserName(api_search_Uename)
    if result!=[]:
        headers=[x[0] for x in cursor.description] # 抓取表頭資訊
        #0-id、1-name、2-username
        data={headers[0]:result[0][0],headers[1]:result[0][1],headers[2]:result[0][2]} # 轉dict
        # 轉物件格式
        data_all={"data":data}
        # 轉json格式 
        json.dumps(data_all)
        return data_all # 轉json      
    else:  
        data_all={"data":None} # 讓內容再包裹成data的值
        json.dumps(data_all)
        return data_all

# api更新姓名
@app.route("/api/member",methods=["POST"])# 用post方法
def apiChangeUserName():
    # 檢查是否用指定的content_type連線
    if request.content_type!= "application/json":
        return Response(response="錯誤的格式", status=400)

    # 抓取api進入的資料
    api_changeUserName=request.get_json()
    # 抓取member.html網頁提交的更新資料，input的屬性name屬性
    htm_changeUserName=request.args.get("changeUserName")


    if api_changeUserName!=None:
        #api的"name"帶入
        newUserName=api_changeUserName['name']
    elif htm_changeUserName!=None:
        newUserName=htm_changeUserName
    else:
        return "沒有要更新的資料"
    return changeUserNamef(newUserName)


# 登出
@app.route("/signout")
def signout():
    # 移除 session 中的會員資訊
    del session["name"]
    return redirect("/")

app.run(port=3000)
