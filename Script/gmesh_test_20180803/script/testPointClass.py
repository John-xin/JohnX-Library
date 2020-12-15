import rhinoscriptsyntax as rs
import os
from pack.Point import *
import sqlite3

pt1 = (1,1,1)
pt2 = (1,1,1)


dict={}
dict.update({pt1:'1111'})
dict.update({pt2:'2222'})

conn=sqlite3.connect('test.db')
c=conn.cursor()

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS testTable(id REAL, data TEXT, keyword TEXT, value REAL)')
    
def data_entry():
    c.execute("INSERT INTO testTable VALUES(21212,'2012-4-1','python',5)")
    conn.commit()
    c.close()
    conn.close()
    
create_table()
data_entry()