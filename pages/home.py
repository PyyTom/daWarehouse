import sqlite3,datetime
from flet import *
from flet_core import Column
from flet_route import Params,Basket
def Home(page:Page,params:Params,basket:Basket):
    def list_it(e):
        c_edit.controls,c_items.controls=[],[]
        b_add.disabled=False
        db=sqlite3.connect('db.db')
        c_list.controls=[Row([TextButton(row,on_click=lambda x,id=row[-2]:edit_it(id))],width=700,scroll=ScrollMode.ALWAYS) for row in db.execute('select * from '+dd.value).fetchall()]
        db.close()
        page.update()
    def edit_it(id):
        # BUILDING EDITOR
        c_edit.controls,t_id.value=[],id
        db=sqlite3.connect('db.db')
        for label in db.execute('select name from pragma_table_info("'+dd.value+'")').fetchall():
            if label[0]=='ID' or label[0]=='USER' or label[0]=='DATE':pass
            elif label[0]=='ENTITY' and dd.value=='ORDERS':c_edit.controls.append(Dropdown(options=[dropdown.Option(supplier[0]) for supplier in db.execute('select NAME from SUPPLIERS group by NAME').fetchall()]))
            elif label[0]=='ENTITY' and dd.value=='BOOKINGS':c_edit.controls.append(Dropdown(options=[dropdown.Option(customer[0]) for customer in db.execute('select NAME from CUSTOMERS group by NAME').fetchall()]))
            else:c_edit.controls.append(TextField(label=label[0],width=600,height=30,disabled=False))
        if dd.value=='ORDERS' or dd.value=='BOOKINGS':
            c_edit.controls.append(r_add)
            c_items.controls=[TextButton(item[0]) for item in db.execute('select * from '+dd.value+' where ID=?',(id,)).fetchall()]
            n=1
        else:n=0
        # SAVING OR UPDATING COMMANDS
        if id!='':
            values =db.execute('select * from ' + dd.value + ' where ID=?', (id,)).fetchone()
            r_commands.controls=[t_id,b_save,b_delete]
            for field in c_edit.controls:
                if values[n]!='DATE':
                    field.value=values[n]
                    n+=1
        else:r_commands.controls=[b_save]
        db.close()
        page.update()
    def save(e):
        data = []
        db = sqlite3.connect('db.db')
        if dd.value=='ORDERS' or dd.value=='BOOKINGS':
            for item in c_items.controls:
                data = [datetime.datetime.today().strftime('%Y-%m,%d')]
                for d in c_edit.controls:
                    if d._get_control_name()=='dropdown':data.append(d.value)
                for field in item.text:data.append(field)
                data.append(t_user.value)
            db.execute('insert into '+dd.value+'(DATE,ENTITY,NAME,LOT,PRICE,QUANTITY,USER) values(?,?,?,?,?,?,?)',data)
            db.commit()
            if db.execute('select * from STOCK where NAME=? and LOT=?',(data[2],data[3],)).fetchall()==[]:
                db.execute('insert into STOCK(SUPPLIER,NAME,LOT,COST,QUANTITY) values(?,?,?,?,?)',(data[1],data[2],data[3],data[4],data[5],))
            else:
                if dd.value=='ORDERS':db.execute('update STOCK set QUANTITY=QUANTITY+? where NAME=? and LOT=?',(data[5],data[2],data[3],))
                elif dd.value== 'BOOKINGS': db.execute('update STOCK set QUANTITY=QUANTITY-? where NAME=? and LOT=?',(data[5],data[2], data[3],))
            db.commit()
        else:
            for d in c_edit.controls:
                if d.label!='ID' and d.label!='USER':data.append(d.value)
            data.append(t_user.value)
            if dd.value=='SUPPLIERS' or dd.value=='CUSTOMERS':
                if t_id.value=='':
                    db.execute('insert into '+dd.value+'(NAME, DNI, CIF, ADDRESS, CAP, CITY, COUNTY, STATE, PHONE, EMAIL, WEBSITE,USER) values(?,?,?,?,?,?,?,?,?,?,?,?)',data)
                else:
                    data.append(t_id.value)
                    db.execute('update '+dd.value+' set NAME=?, DNI=?, CIF=?, ADDRESS=?, CAP=?, CITY=?, COUNTY=?, STATE=?, PHONE=?, EMAIL=?, WEBSITE=?,USER=? where ID=?',data)
                db.commit()
        db.close()
        list_it('')
        page.update()
    def delete(e):
        db=sqlite3.connect('db.db')
        db.execute('delete from '+dd.value+' where ID=?',(t_id.value,))
        db.commit()
        db.close()
        list_it('')
        page.update()
    def add(e):
        def remove(e):
            c_items.controls.remove(e.control)
            page.update()
        item=[]
        for d in c_edit.controls:
            if d._get_control_name()=='textfield':item.append(d.value)
        c_items.controls.append(TextButton(item,on_click=remove))
        page.update()
    dialog=AlertDialog()
    page.dialog=dialog
    # BUILDING LIST
    dd=Dropdown(label='LISTS',options=[dropdown.Option(lst) for lst in ['SUPPLIERS', 'ORDERS', 'STOCK', 'CUSTOMERS', 'BOOKINGS']],on_change=list_it)
    b_add=IconButton(icon=icons.ADD,icon_color='green',disabled=True,on_click=lambda _:edit_it(''))
    c_list=Column(width=700,height=650,scroll=ScrollMode.ALWAYS)
    # BUILDING DETAILS
    t_id=Text()
    r_commands=Row([t_id],alignment=MainAxisAlignment.CENTER)
    r_add=Row([ElevatedButton('ADD',on_click=add)],alignment=MainAxisAlignment.CENTER)
    c_edit=Column(width=700,height=300,scroll=ScrollMode.ALWAYS)
    c_items = Column(width=700, height=300, scroll=ScrollMode.ALWAYS)
    c_details=Column([c_edit,r_commands,Divider(),c_items],width=700,height=650)
    b_save=ElevatedButton('SAVE',on_click=save)
    b_delete=ElevatedButton('DELETE',on_click=delete)
    db=sqlite3.connect('db.db')
    t_user=Text(db.execute('select USER from USERS where ON_AIR="v"').fetchone()[0])
    db.close()
    return View('/home',controls=[Row([Text('USER :'),t_user,IconButton(on_click=lambda _:page.go('/'),icon=icons.EXIT_TO_APP_OUTLINED,icon_size=50,icon_color='red')],alignment=MainAxisAlignment.END),Divider(),
                                  Row([dd,b_add,Text(width=500)],alignment=MainAxisAlignment.CENTER),
                                  Row([c_list,VerticalDivider(),c_details],height=700)])