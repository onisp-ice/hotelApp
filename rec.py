import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from datetime import datetime
import sqlite3
import connect


class receptionist_app:

    def __init__(self, root):
        self.root = root

        self.root.title("Receptionist Account")
        self.root.geometry("1350x1200+0+0")
        self.root.configure(bg="#ffffff")

        self.style = ttk.Style()

        self.main_ui()

   
    def main_ui(self):

        self.head = ttk.Frame(self.root, padding=12)
        self.head.pack(fill="x")

        ttk.Label(
            self.head,
            text="HOTEL MANAGEMENT SYSTEM",
            font=("Verdana", 20, "bold"),
            foreground="#000000"
        ).pack(side="top")

        ttk.Label(
            self.head,
            text="Receptionist Account",
            font=("Verdana", 10, "bold")
        ).pack(side="right", padx=10)

        ttk.Button(
            self.head,text="Log Out",command=self.logout
                        
            
        ).pack(side="right", padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(
            fill="both",expand=True,padx=10,pady=5
                                   
                        
        )

        # Rooms
        self.rooms_tab = ttk.Frame(
            self.notebook,
            padding=15
        )

        # Check-in
        self.checkin_tab = ttk.Frame(
            self.notebook, padding=15
           
        )

        # Check-out
        self.checkout_tab = ttk.Frame(
            self.notebook,padding=15
            
        )

        self.notebook.add(
            self.rooms_tab, text="Rooms"
           
        )

        self.notebook.add(
            self.checkin_tab,
            text="Check-In / Allocation"
        )

        self.notebook.add(
            self.checkout_tab,
            text="Check-Out"
        )

        self.build_rooms()
        self.build_checkin()
        self.build_checkout()

    
    def build_rooms(self):

        form = ttk.LabelFrame(
            self.rooms_tab,
            text="Room Information",padding=12
            
        )
        form.pack(fill="x")

        ttk.Label(
            form,
            text="Room No"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.room_no = ttk.Entry(
            form, width=15
            
        )
        self.room_no.grid(
            row=0,column=1,padx=5
                
            
        )

        ttk.Label(
            form,
            text="Room Type"
        ).grid(row=0, column=2, padx=5)

        rooms = [
            "Single Room",
            "Double Room",
            "Deluxe Room",
            "Suite Room"
        ]

        self.room_type = ttk.Combobox(
            form,
            values=rooms,state="readonly",width=15
                        
            
        )

        self.room_type.grid(
            row=0,column=3, padx=5
                       
            
        )

        self.room_type.set("Single Room")

        ttk.Label(
            form,
            text="Price / Night"
        ).grid(row=0, column=4, padx=5)

        self.room_price = ttk.Entry(
            form,
            width=15
        )

        self.room_price.grid(
            row=0,
            column=5,
            padx=5
        )

        ttk.Button(
            form,
            text="Add Room",
            command=self.add_rooms
        ).grid(
            row=0,
            column=6,
            padx=10
        )

        ttk.Button(
            form,
            text="Delete Room",
            command=self.delete_rooms
        ).grid(
            row=0,
            column=7,
            padx=5
        )

        columns = (
            "id",
            "room_no",
            "type",
            "price",
            "status"
        )

        self.room_tree = ttk.Treeview(
            self.rooms_tab,columns=columns, show="headings",height=18
           
        
        )

        headings = {
            "id": "Position",
            "room_no": "Room No",
            "type": "Type",
            "price": "Price/Night",
            "status": "Status"
        }

        for column in columns:

            self.room_tree.heading(
                column,text=headings[column]
                
            )

            self.room_tree.column(
                column, width=150
               
            )

        self.room_tree.pack(
            fill="both",expand=True, pady=12
            
           
        )

        self.refresh_rooms()

    def refresh_rooms(self):

        for item in self.room_tree.get_children():
            self.room_tree.delete(item)

        rows = connect.cur.execute(
            "SELECT * FROM rooms ORDER BY room_no"
        ).fetchall()

        for room in rows:

            self.room_tree.insert(
                "",
                "end",
                values=(
                    room[0],
                    room[1],
                    room[2],
                    f"₦{room[3]:,.2f}",
                    room[4]
                )
            )

    def add_rooms(self):

        room_no = self.room_no.get().strip()
        room_type = self.room_type.get().strip()
        price_text = self.room_price.get().strip()

        if not room_no or not price_text:

            msg.showwarning(
                "Validation",
                "Enter room number and price."
            )

            return

        try:
            price = float(price_text)

        except ValueError:

            msg.showerror(
                "Validation", "Price must be numeric."
               
            )

            return

        try:

            connect.cur.execute(
                """
                INSERT INTO rooms
                (room_no, room_type, price)
                VALUES (?, ?, ?)
                """,
                (
                    room_no,
                    room_type,
                    price
                )
            )

            connect.con.commit()

            msg.showinfo(
                "Success",
                "Room added successfully."
            )

            self.room_no.delete(
                0, "end"
               
            )

            self.room_price.delete(
                0,"end"
                
            )

            self.refresh_rooms()
            self.refresh_checkin_options()

        except sqlite3.IntegrityError:

            msg.showerror(
                "Error",
                "Room number already exists."
            )

    def delete_rooms(self):

        selected = self.room_tree.selection()

        if not selected:

            msg.showwarning(
                "Select",
                "Select a room first."
            )

            return

        values = self.room_tree.item(
            selected[0]
        )["values"]

        room_id = values[0]

        confirm = msg.askyesno(
            "Delete Room",
            "Are you sure you want to delete this room?"
        )

        if not confirm:
            return

        active = connect.cur.execute(
            """
            SELECT id
            FROM bookings
            WHERE room_id=?
            AND status='Checked In'
            """,
            (room_id,)
        ).fetchone()

        if active:

            msg.showerror(
                "Error",
                "Occupied rooms cannot be deleted."
            )

            return

        connect.cur.execute(
            "DELETE FROM rooms WHERE id=?",
            (room_id,)
        )

        connect.con.commit()

        msg.showinfo(
            "Success","Room deleted successfully."
            
        )

        self.refresh_rooms()
        self.refresh_checkin_options()

   
    def build_checkin(self):

        form = ttk.LabelFrame(
            self.checkin_tab,
            text="Room Allocation and Guest Check-In",
            padding=15
        )

        form.pack(fill="x")

        ttk.Label(
            form,
            text="Guest"
        ).grid(
            row=0, column=0, padx=5,  pady=8
                                  
            
        )

        self.checkin_guest = ttk.Combobox(
            form, state="readonly",width=35
                        

        )

        self.checkin_guest.grid(
            row=0, column=1,  padx=5
                      
           
        )

        ttk.Label(
            form,
            text="Available Room"
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        self.checkin_room = ttk.Combobox(
            form,
            state="readonly",
            width=40
        )

        self.checkin_room.grid(
            row=0,
            column=3,
            padx=5
        )

        ttk.Label(
            form,
            text="Adults"
        ).grid(
            row=1,
            column=0,
            padx=5
        )

        self.adults = ttk.Spinbox(
            form, from_=1, to=20,width=8
                                    
                       
           
        )

        self.adults.grid(
            row=1,  column=1, sticky="w", padx=5
                                   
                      
  
        )

        self.adults.set(1)

        ttk.Label(
            form,
            text="Children"
        ).grid(
            row=1,column=2,   padx=5
                     
            
        )

        self.children = ttk.Spinbox(
            form,
            from_=0,
            to=20,
            width=8
        )

        self.children.grid(
            row=1,
            column=3,
            sticky="w",
            padx=5
        )

        self.children.set(0)

        ttk.Button(
            form,
            text="CHECK IN / ALLOCATE ROOM",
            command=self.check_in
        ).grid(
            row=2,
            column=0,
            columnspan=4,
            pady=15
        )

        ttk.Button(
            form,
            text="Refresh Available Rooms",
            command=self.refresh_checkin_options
        ).grid(
            row=2,
            column=4,
            padx=10
        )

        columns = (
            "id",
            "guest",
            "room",
            "type",
            "checkin",
            "adults",
            "children",
            "total",
            "status"
        )

        self.booking_tree = ttk.Treeview(
            self.checkin_tab,
            columns=columns,
            show="headings",
            height=15
        )

        headings = {
            "id": "ID",
            "guest": "Guest",
            "room": "Room",
            "type": "Type",
            "checkin": "Check-In",
            "adults": "Adults",
            "children": "Children",
            "total": "Total",
            "status": "Status"
        }

        widths = {
            "id": 50,
            "guest": 180,
            "room": 80,
            "type": 120,
            "checkin": 150,
            "adults": 70,
            "children": 80,
            "total": 100,
            "status": 100
        }

        for column in columns:

            self.booking_tree.heading(
                column,
                text=headings[column]
            )

            self.booking_tree.column(
                column,
                width=widths[column]
            )

        self.booking_tree.pack(
            fill="both",
            expand=True,
            pady=12
        )

        self.refresh_checkin_options()
        self.refresh_checkin_bookings()

    def refresh_checkin_options(self):

        guests = connect.cur.execute(
            """
            SELECT id, full_name, phone, email, address
            FROM guests
            ORDER BY full_name
            """
        ).fetchall()

        rooms = connect.cur.execute(
            """
            SELECT id, room_no, room_type, price
            FROM rooms
            WHERE status='Available'
            ORDER BY room_no
            """
        ).fetchall()

        self.checkin_guest["values"] = [
            f"{g[0]} | {g[1]} | {g[2]} | {g[3]} | {g[4]}"
            for g in guests
        ]

        self.checkin_room["values"] = [
            f"{r[0]} | Room {r[1]} | {r[2]} | ₦{r[3]:,.2f}"
            for r in rooms
        ]

        if self.checkin_guest["values"]:
            self.checkin_guest.current(0)

        if self.checkin_room["values"]:
            self.checkin_room.current(0)

    def check_in(self):

        guest_value = self.checkin_guest.get()
        room_value = self.checkin_room.get()

        if not guest_value or not room_value:

            msg.showwarning(
                "Validation",
                "Select a guest and an available room."
            )

            return

        guest_id = int(
            guest_value.split("|")[0].strip()
        )

        room_id = int(
            room_value.split("|")[0].strip()
        )

        try:

            adults = int(
                self.adults.get()
            )

            children = int(
                self.children.get()
            )

        except ValueError:

            msg.showerror(
                "Validation",
                "Adults and children must be numbers."
            )

            return

        room = connect.cur.execute(
            """
            SELECT *
            FROM rooms
            WHERE id=?
            AND status='Available'
            """,
            (room_id,)
        ).fetchone()

        if not room:

            msg.showerror(
                "Error",
                "Room is no longer available."
            )

            self.refresh_checkin_options()

            return

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        connect.cur.execute(
            """
            INSERT INTO bookings
            (
                guest_id,
                room_id,
                checkin,
                adults,
                children,
                status,
                total,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, 'Checked In', ?, ?)
            """,
            (
                guest_id,
                room_id,
                now,
                adults,
                children,
                room[3],
                now
            )
        )

        connect.cur.execute(
            """
            UPDATE rooms
            SET status='Occupied'
            WHERE id=?
            """,
            (room_id,)
        )

        connect.con.commit()

        msg.showinfo(
            "Check-In Successful",
            f"Guest checked in successfully.\n\n"
            f"Room: {room[1]}\n"
            f"Rate: ₦{room[3]:,.2f} per night"
        )

        self.refresh_checkin_options()
        self.refresh_rooms()
        self.refresh_checkin_bookings()
        self.refresh_checkout()

    def refresh_checkin_bookings(self):

        for item in self.booking_tree.get_children():
            self.booking_tree.delete(item)

        rows = connect.cur.execute(
            """
            SELECT
                b.id,
                g.full_name,
                r.room_no,
                r.room_type,
                b.checkin,
                b.adults,
                b.children,
                b.total,
                b.status
            FROM bookings b
            JOIN guests g
                ON g.id = b.guest_id
            JOIN rooms r
                ON r.id = b.room_id
            WHERE b.status='Checked In'
            ORDER BY b.id DESC
            """
        ).fetchall()

        for b in rows:

            self.booking_tree.insert(
                "",
                "end",
                values=(
                    b[0],
                    b[1],
                    b[2],
                    b[3],
                    b[4],
                    b[5],
                    b[6],
                    f"₦{b[7]:,.2f}",
                    b[8]
                )
            )

    
    def build_checkout(self):

        ttk.Label(
            self.checkout_tab,
            text="Active Guests / Check-Out",
            font=("Arial", 18, "bold")
        ).pack(anchor="w")

        columns = (
            "id",
            "guest",
            "room",
            "type",
            "checkin",
            "nights",
            "rate",
            "total",
            "status"
        )

        self.checkout_tree = ttk.Treeview(
            self.checkout_tab,
            columns=columns,
            show="headings",
            height=15
        )

        headings = {
            "id": "Booking",
            "guest": "Guest",
            "room": "Room",
            "type": "Type",
            "checkin": "Check-In",
            "nights": "Nights",
            "rate": "Rate",
            "total": "Estimated Total",
            "status": "Status"
        }

        widths = {
            "id": 70,
            "guest": 190,
            "room": 80,
            "type": 120,
            "checkin": 150,
            "nights": 80,
            "rate": 100,
            "total": 130,
            "status": 100
        }

        for column in columns:

            self.checkout_tree.heading(
                column,
                text=headings[column]
            )

            self.checkout_tree.column(
                column,
                width=widths[column]
            )

        self.checkout_tree.pack(
            fill="both",
        
            pady=15
        )

        ttk.Button(
            self.checkout_tab,
            text="CHECK OUT SELECTED GUEST",
            command=self.check_out
        ).pack(
            anchor="e"
        )

        self.refresh_checkout()

    def refresh_checkout(self):

        for item in self.checkout_tree.get_children():
            self.checkout_tree.delete(item)

        rows = connect.cur.execute(
            """
            SELECT
                b.id,
                g.full_name,
                r.room_no,
                r.room_type,
                b.checkin,
                r.price,
                b.status
            FROM bookings b
            JOIN guests g
                ON g.id=b.guest_id
            JOIN rooms r
                ON r.id=b.room_id
            WHERE b.status='Checked In'
            ORDER BY b.id DESC
            """
        ).fetchall()

        today = datetime.now().date()

        for b in rows:

            checkin_date = datetime.strptime(
                b[4],
                "%Y-%m-%d %H:%M:%S"
            ).date()

            nights = max(
                1,
                (today - checkin_date).days
            )

            estimated = nights * b[5]

            self.checkout_tree.insert(
                "",
                "end",
                values=(
                    b[0],
                    b[1],
                    b[2],
                    b[3],
                    b[4],
                    nights,
                    f"₦{b[5]:,.2f}",
                    f"₦{estimated:,.2f}",
                    b[6]
                )
            )

    def check_out(self):

        selected = self.checkout_tree.selection()

        if not selected:

            msg.showwarning(
                "Select",
                "Select at least one booking to check out."
            )

            return

        bookings_selected = []

        for item in selected:

            values = self.checkout_tree.item(
                item
            )["values"]

            bookings_selected.append({
                "id": values[0],
                "guest": values[1],
                "room_no": values[2]
            })

        details = "\n".join(
            f"• {b['guest']} - Room {b['room_no']}"
            for b in bookings_selected
        )

        confirm = msg.askyesno(
            "Confirm Check-Out",
            f"Check out the following "
            f"{len(bookings_selected)} booking(s)?\n\n"
            f"{details}"
        )

        if not confirm:
            return

        try:

            checkout = datetime.now()

            checkout_str = checkout.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            checkout_results = []

            for b in bookings_selected:

                booking = connect.cur.execute(
                    """
                    SELECT room_id, checkin
                    FROM bookings
                    WHERE id=?
                    AND status='Checked In'
                    """,
                    (b["id"],)
                ).fetchone()

                if not booking:
                    continue

                checkin_dt = datetime.strptime(
                    booking["checkin"],
                    "%Y-%m-%d %H:%M:%S"
                )

                nights = max(
                    1,
                    (checkout.date() - checkin_dt.date()).days
                )

                room = connect.cur.execute(
                    """
                    SELECT price, room_no
                    FROM rooms
                    WHERE id=?
                    """,
                    (booking["room_id"],)
                ).fetchone()

                if not room:
                    continue

                final_total = nights * room["price"]

                connect.cur.execute(
                    """
                    UPDATE bookings
                    SET checkout=?,
                        status='Checked Out',
                        total=?
                    WHERE id=?
                    """,
                    (
                        checkout_str,
                        final_total,
                        b["id"]
                    )
                )

                connect.cur.execute(
                    """
                    UPDATE rooms
                    SET status='Available'
                    WHERE id=?
                    """,
                    (booking["room_id"],)
                )

                checkout_results.append({
                    "guest": b["guest"],
                    "room_no": room["room_no"],
                    "nights": nights,
                    "total": final_total
                })

            connect.con.commit()

            if not checkout_results:

                msg.showerror(
                    "Error",
                    "None of the selected bookings are still active."
                )

                return

            grand_total = sum(
                item["total"]
                for item in checkout_results
            )

            result = ""

            for item in checkout_results:

                result += (
                    f"Guest: {item['guest']}\n"
                    f"Room: {item['room_no']}\n"
                    f"Nights: {item['nights']}\n"
                    f"Bill: ₦{item['total']:,.2f}\n"
                    f"{'-' * 35}\n"
                )

            result += (
                f"\nGRAND TOTAL: "
                f"₦{grand_total:,.2f}"
            )

            msg.showinfo(
                "Check-Out Complete",
                f"{len(checkout_results)} "
                f"booking(s) checked out successfully.\n\n"
                f"{result}"
            )

            self.refresh_checkout()
            self.refresh_rooms()
            self.refresh_checkin_options()
            self.refresh_checkin_bookings()

        except Exception as e:

            connect.con.rollback()

            msg.showerror(
                "Check-Out Error",
                f"An error occurred during check-out:\n\n{e}"
            )

  
    def logout(self):

        if msg.askyesno(
            "Logout",
            "Are you sure you want to log out?"
        ):

            self.root.destroy()


root = tk.Tk()

app = receptionist_app(root)

root.title("Receptionist Account")
root.geometry('1350x1200+0+0')
root.configure(bg="#0b1120")




root.resizable(0,0)
root.mainloop()