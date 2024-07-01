import sqlite3
db=sqlite3.connect('db.db')
db.execute('create table if not exists USERS(USER,PASSWORD,ON_AIR)')
db.execute('create table if not exists SUPPLIERS(NAME, DNI, CIF, ADDRESS, CAP, CITY, COUNTY, STATE, PHONE, EMAIL, WEBSITE,ID integer primary key autoincrement,USER)')
db.execute('create table if not exists CUSTOMERS(NAME, DNI, CIF, ADDRESS, CAP, CITY, COUNTY, STATE, PHONE, EMAIL, WEBSITE,ID integer primary key autoincrement,USER)')
db.execute('create table if not exists STOCK(SUPPLIER,NAME,LOT,COST float,QUANTITY integer)')
db.execute('create table if not exists ORDERS(DATE,ENTITY,NAME,LOT,PRICE float,QUANTITY integer,ID integer primary key autoincrement,USER)')
db.execute('create table if not exists BOOKINGS(DATE,ENTITY,NAME,LOT,PRICE float,QUANTITY integer,ID integer primary key autoincrement,USER)')
db.close()
from flet import *
from flet_route import Routing,path
from pages.login import Login
from pages.home import Home
def main(page:Page):
    page.window_full_screen=True
    page.theme_mode='light'
    app_routes=[path(url='/',view=Login,clear=True),
                path(url='/home',view=Home,clear=True)]
    Routing(page=page,app_routes=app_routes)
    page.go(page.route)
app(target=main)