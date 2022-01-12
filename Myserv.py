from os import close
import tornado.ioloop
import tornado.web
import psycopg2

conn  = psycopg2.connect(dbname  = 'postgres', user = 'postgres', password = '6626')
cur = conn.cursor()
cur.execute("SELECT * FROM usernames")
end = cur.fetchall()
print(end)
conn.commit()

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        try:
            return tornado.escape.xhtml_escape(self.get_secure_cookie("user"))
            
        except TypeError:
            pass
                
class MainHandler(BaseHandler):
    def get(self):
        cookie_user = self.current_user
        cookie_password = self.get_secure_cookie('password')

        if cookie_user is None and cookie_password is None:
            self.redirect("/login")
            return
        cookie_password = cookie_password.decode("UTF-8")
        cur.execute("SELECT username, passwd FROM usernames")
        temp = cur.fetchall()
        if not any(tuple(temp[i][0] == cookie_user and temp[i][1] == cookie_password for i in range(len(temp)))):
        # file = open('name.txt', 'r')
        # if not any(tuple(cookie_user + ":" + cookie_password == line.replace('\n', "") for line in file)):
            self.redirect("/login")
            return
        self.write("Hello," + " " + cookie_user)   


class LoginHandler(BaseHandler):

    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("password")
        self.render('login.html')

    def post(self):
        a = False
        cur.execute("SELECT username, passwd FROM usernames")
        temp = cur.fetchall()
        for i in range(len(temp)):
            if self.get_argument("username") == temp[i][0] and self.get_argument("password") == temp[i][1]:
                a = True
                break
        # file = open('name.txt', 'r')
        # for line in file:
        #     if self.get_argument("username") == line.replace('\n', "").split(":")[0] and self.get_argument("password") == line.replace('\n', "").split(":")[1]:
        #             a = True
        #             break
                    
        if a :
            self.set_secure_cookie("user", self.get_argument("username"))
            self.set_secure_cookie("password", self.get_argument("password"))
            self.redirect("/")
        else:
            self.redirect("/reg")
            print("incorrect")

class RegHandler(BaseHandler):
    def get(self):
        self.render('reg.html')

    def post(self):
        user = self.get_argument("username")
        password = self.get_argument("password")
        cur.execute("SELECT username, passwd FROM usernames")
        temp = cur.fetchall()
        if not any(tuple(temp[i][0] == user and temp[i][1] == password for i in range(len(temp)))): 
            cur.execute("INSERT INTO usernames (username, passwd) VALUES (%s, %s)", (user, password))
            conn.commit()
            self.redirect('/login')
        else:
            self.redirect('/reg')
            print("incorrect")
        # file = open('name.txt', 'r+')
        # if self.get_argument("username") and self.get_argument("password") and not any(tuple(self.get_argument("username") + ":" + self.get_argument("password") == line.replace('\n', "") for line in file)):
        #     file.write(self.get_argument("username") + ":" + self.get_argument("password") + '\n')
        #     self.redirect('/login')
        # else :
        #     self.redirect('/reg')
        #     print("incorrect")
        # file.close()

if __name__ == "__main__":
    application = tornado.web.Application([(r"/", MainHandler),(r"/login", LoginHandler),(r'/reg', RegHandler),], cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=")
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()