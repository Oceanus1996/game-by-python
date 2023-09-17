import tkinter as tk
from tkinter import filedialog # For masters task
from typing import Callable, Union, Optional
from a3_support import *
from model import *
from constants import *

# Implement your classes here

def play_game(root: tk.Tk, map_file: str) -> None:
    """ Create the window, ensure it displays when the program is run
        and set its title"""
    # 1. Construct the controller instance
    game =FarmGame(root,map_file)
    # 2. Keep the root window open and listen for events
    root.mainloop()

class InfoBar(AbstractGrid):
    """InfoBar should inherit from AbstractGrid (see a3 support.py). It is a grid with 2 rows and 3
       columns, which displays information to the user about the number of days elapsed in the game,
       as well as the player’s energy and health. The InfoBar should span the entire width of the farm
       and inventory combined."""
    def __init__(self,master:tk.Tk or tk.Frame):
        """
              sets up this InfoBar to be an AbstractGrid with the appropriate number of rows and columns,
              and the width and height
              """
        super().__init__(master,dimensions=(2,3),size=(FARM_WIDTH + INVENTORY_WIDTH,INFO_BAR_HEIGHT))

    def redraw(self, day:int,money:int,energy:int):
        """ Clears the InfoBar and redraws it to display the provided day, money, and energy.
            Paras: day: new day
                   money: update money
                   energy:reset it"""
        self.clear()
        self.annotate_position((0, 0), "Day:",font=HEADING_FONT )
        self.annotate_position((0, 1), "Money:",font=HEADING_FONT )
        self.annotate_position((0, 2), "Energy:",font=HEADING_FONT )
        self.annotate_position((1, 0), day)
        self.annotate_position((1, 1), "$"+str(money))
        self.annotate_position((1, 2), energy)


class FarmView(AbstractGrid):
    """
    FarmView should inherit from AbstractGrid (see a3 support.py). The FarmView is a grid displaying
     the farm map,player, and plants.
    """
    def __init__ (self, master: tk.Tk | tk.Frame, dimensions: tuple[int, int], size:
                   tuple[int, int], **kwargs) -> None:
        """
         Sets up the FarmView to be an AbstractGrid with the appropriate dimensions and size, and 
         creates an instance attribute of an empty dictionary to be used as an image cache.
        Args:
            master: tk or frame
            dimensions: the separate height and width
            size: the whole height and width
        """
        super().__init__(master,dimensions=dimensions,size=size)
        self._cache={} #cache
        for i_value in IMAGES.values():
            i_path = "images/" + i_value
            get_image(i_path, self.get_cell_size(), self._cache)

    def redraw(self, ground: list[str],
               plants: dict[tuple[int, int],'Plant'],
               player_position: tuple[int, int],
               player_direction: str) -> None:
        """
        Clears the farm view, then creates (on the FarmView instance) the images for the ground,
        then the plants, the the player
        Args:
            ground: ground tuple
            plants: plants list
            player_position: the tuple with position's x and y
            player_direction: the direction of player

        Returns:show the new canva
        """
        self.clear()

        #map
        for i,row in enumerate(ground):
            for j,column in enumerate(row):
                pixel_x,pixel_y=self.get_midpoint((i,j))#position
                col_name="images/"+IMAGES[column]#path
                col_image=get_image(col_name, self.get_cell_size(), self._cache)
                self.create_image(pixel_x,pixel_y,image=col_image)

        if plants =={}:
            pass
        else:
            for m,plant in plants.items():
                pixel_x1,pixel_y1=self.get_midpoint(m)
                plant_name="images/"+get_plant_image_name(plant)#path
                plant_image=get_image(plant_name,self.get_cell_size(),self._cache)
                self.create_image(pixel_x1, pixel_y1,image=plant_image)

        #player
        player_dirt="images/player_"+player_direction+".png"
        player_image = get_image(player_dirt,self.get_cell_size(),self._cache)
        pixel_x2,pixel_y2=self.get_midpoint(player_position)
        self.create_image(pixel_x2, pixel_y2,image=player_image)

    def clear_cache(self):
        self._cache={ }

class ItemView(tk.Frame):
    """
    ItemView should inherit from tk.Frame. The ItemView is a frame displaying relevant
    information and buttons for a single item. There are 6 items available in the game
     (see the ITEMS constant in constants.py).
    """
    def __init__(self,
                 master: tk.Tk|tk.Frame,
                 item_name: str,
                 amount: int,
                 select_command:Optional[Callable[[str], None]] = None,
                 sell_command: Optional[Callable[[str],None]] = None,
                 buy_command: Optional[Callable[[str], None]] = None)-> None:
        """
          Sets up ItemView to operate as a tk.Frame, and creates all internal widgets.
        Args:
            master: tk.frame
            item_name: the plants or plants seed name
            amount: the amount of item
            select_command: when click the itemview
            sell_command: when click the sell button
            buy_command: when click the buy button
        """
        super().__init__(master,bd=1,relief=tk.RAISED)

        self._item_name=item_name
        self._amount=amount

        #divide to 2 frame and set different label and button in it.
        self._text_frame=tk.Frame(self,bg=INVENTORY_COLOUR)
        self._text_frame.pack(side="left",fill="both",expand=True)
        self._button_frame = tk.Frame(self,bg=INVENTORY_COLOUR)
        self._button_frame.pack(side="right",fill="both",expand=True)
        self._name_label=tk.Label(self._text_frame,text=str(self._item_name)+": "+ str(self._amount),
                                  bg=INVENTORY_COLOUR)
        self._name_label.pack(side="top",fill="both")
        self._sell_label = tk.Label(self._text_frame, text="Sell price: $"+str(SELL_PRICES[self._item_name]),
                                    bg=INVENTORY_COLOUR)
        self._sell_label.pack(side="top",fill="both")

        if self._item_name in SEEDS:
            self._buy_label = tk.Label(self._text_frame, text="Buy price: $"+str(BUY_PRICES[self._item_name]),
                                       bg=INVENTORY_COLOUR)
            self._buy_label.pack(side="top")
        else:
            self._buy_label = tk.Label(self._text_frame, text="Buy price: $N/A",bg=INVENTORY_COLOUR)
            self._buy_label.pack(side="top")

        if self._item_name  in SEEDS:
            self._buy_button=tk.Button(self._button_frame,text="Buy",command=buy_command)
            self._buy_button.pack(side="left")
        else:
            pass

        self._sell_button=tk.Button(self._button_frame,text="Sell", command=sell_command)
        self._sell_button.pack(side="left")

        #command bind
        self.bind("<Button-1>",select_command)
        self._text_frame.bind("<Button-1>", select_command)
        self._button_frame.bind("<Button-1>", select_command)
        self._buy_label.bind("<Button-1>", select_command)
        self._button_frame.bind("<Button-1>", select_command)
        self._name_label.bind("<Button-1>", select_command)
        self._sell_label.bind("<Button-1>", select_command)

    def update(self, amount: int, selected: bool = False) -> None:
        """
        Updates the text on the label, and the colour of this ItemView appropriately.
        Args:
            amount: the amount of the plant
            selected: whether selected or not
        Returns: show new darw
        """
        self._amount=amount
        self._name_label.config(text=str(self._item_name) + ": " + str(self._amount))

        #if selected or not
        if selected == True:
            self.config(bg=INVENTORY_SELECTED_COLOUR)
            self._button_frame.config(bg=INVENTORY_SELECTED_COLOUR)
            self._name_label.config(bg=INVENTORY_SELECTED_COLOUR)
            self._sell_label.config(bg=INVENTORY_SELECTED_COLOUR)
            self._buy_label.config(bg=INVENTORY_SELECTED_COLOUR)
            self._text_frame.config(bg=INVENTORY_SELECTED_COLOUR)
        else:
            self.config(bg=INVENTORY_COLOUR)
            self._button_frame.config(bg=INVENTORY_COLOUR)
            self._name_label.config(bg=INVENTORY_COLOUR)
            self._sell_label.config(bg=INVENTORY_COLOUR)
            self._buy_label.config(bg=INVENTORY_COLOUR)
            self._text_frame.config(bg=INVENTORY_COLOUR)

        #if amount is none
        if amount <= 0:
            self.config(bg=INVENTORY_EMPTY_COLOUR)
            self._button_frame.config(bg=INVENTORY_EMPTY_COLOUR)
            self._name_label.config(bg=INVENTORY_EMPTY_COLOUR)
            self._sell_label.config(bg=INVENTORY_EMPTY_COLOUR)
            self._buy_label.config(bg=INVENTORY_EMPTY_COLOUR)
            self._text_frame.config(bg=INVENTORY_EMPTY_COLOUR)


class  FarmGame():
    """FarmGame is the controller class for the overall game. The controller is responsible for creating and 
       maintaining instances of the model and view classes, event handling, and facilitating communication between
     the model and view classes."""
    def __init__(self, master: tk.Tk, mapfile: str) -> None:
        """
        create title, title banner, farmmodel, the display, the next day button,keypress function,call redrew
        Args:
            master:tk
            mapfile:the map we play
        """
        #title
        title=master.title("Farm Game")
        title_label = master.winfo_toplevel()

        #frame of canva
        frame1=tk.Frame(master)
        frame1.pack(side="top")
        frame2 = tk.Frame(master)
        frame2.pack(side="top",fill="both",expand=True)
        frame3 = tk.Frame(master)
        frame3.pack(side="bottom")
        self._frame2_1=tk.Frame(frame2)
        self._frame2_1.pack(side="left")
        frame2_2 = tk.Frame(frame2)
        frame2_2.pack(side="left",fill="both",expand=True)
        self._master = master

        #header in frame1
        self._farmcache={}
        header_image=get_image("images/header.png",(FARM_WIDTH+INVENTORY_WIDTH,BANNER_HEIGHT),self._farmcache)
        self._header=tk.Label(frame1,image=header_image)
        self._header.pack(side="top")

        #framview in frame2,include inventory and player
        self._model=FarmModel(mapfile)
        self._player=self._model.get_player()
        self._inventory=self._player.get_inventory()
        dimensions=self._model.get_dimensions()
        self._farmview=FarmView(self._frame2_1,dimensions,(FARM_WIDTH,FARM_WIDTH))
        self._farmview.pack(side="left")

        #itemview in frame3
        self._item_views = []
        self._index={}

        for item in ITEMS:
            item_view = ItemView(frame2_2,item,self._inventory.get(item,0),
                                 select_command = lambda _, item=item: self.select_item(item),
                                 buy_command=lambda  item=item: self.buy_item(item),
                                 sell_command=lambda  item=item: self.sell_item(item)
                                 )
            item_view.pack(side="top", fill="both", expand=True)
            self._item_views.append(item_view)
            self._index[item]=item_view

        # navagation bar
        menubar = tk.Menu(master)
        master.config(menu=menubar)  # tell master what its menubar is

        # within the menu bar create the file menu
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)  # tell menubar what its menu is

        # within the file menu create the file processing options
        filemenu.add_command(label="Quit", command=self.quit_game)
        filemenu.add_command(label="Map selection", command=self.open_file)

        #inforbar in frame 3
        self._inforbar = InfoBar(frame3)
        self._inforbar.pack(side="top")
        self._nextday=tk.Button(frame3,text="Next day",command=self.next_day)
        self._nextday.pack(side="top")

        #redrew
        self.redraw()
        master.bind("<KeyPress>",self.handle_keypress)


    def next_day(self):
        """
        turn to next day ,reset energy and plants have grown.
        Returns:a new show canva
        """
        self._model.new_day()
        self._inforbar.redraw(self._model.get_days_elapsed(),
                              self._player.get_money(),
                              self._player.get_energy())
        self._farmview.redraw(self._model.get_map(),
                              self._model.get_plants(),
                              self._player.get_position(),
                              self._player.get_direction())


    def redraw(self) -> None:
        """
        Redraws the entire game based on the current model state.
        Returns:redrew the canva
        """
        self._inforbar.redraw(self._model.get_days_elapsed(),
                              self._player.get_money(),
                              self._player.get_energy())
        self._farmview.redraw(self._model.get_map(),
                              self._model.get_plants(),
                              self._player.get_position(),
                              self._player.get_direction())


        for i in self._index:#if its amount is 0,turn grey
            amount_i=self._player.get_inventory().get(i,0)
            self._index[i].update(int(amount_i),selected=False)

        for item_view in self._index:#if it's selected,trun dark yellow
            if self._player.get_selected_item() is not None:
                select_one = self._player.get_selected_item()
                select_button = self._index[select_one]
                if item_view == select_one:
                    amount=self._player.get_inventory().get(item_view)
                    if amount is None:
                        return
                    select_button.update(amount,selected=True)


    def handle_keypress(self, event: tk.Event) -> None:
        """
        An event handler to be called when a keypress event occurs.
        Args:
            w: turn up
            s: turn down
            a: turn left
            d: turn right
            p:plant the selected seed if it available
            h:harvaset the positions plant if it avaulable
            r: remove the positions plant if it avaulable
            t:till the soil if it is untill
            s:untill the untilled soil if it is soil
        Returns:redrew the all canva
        """

        if event.keysym == "w":
            self._model.move_player(event.keysym)
        elif event.keysym == "s":
            self._model.move_player(event.keysym)
        elif event.keysym == "a":
            self._model.move_player(event.keysym)
        elif event.keysym == "d":
            self._model.move_player(event.keysym)

        position = self._model.get_player_position()
        plant_list = self._model.get_plants()

        if event.keysym == "p":

            if self._player.get_selected_item() is not None:
                if self._player.get_selected_item() in SEEDS:
                    seed_selected=self._player.get_selected_item()
                    position= self._model.get_player_position()
                    map_position=self._model.get_map(),17
                    position_x,position_y=position
                    map_position_x=map_position[0][position_x]
                    map_position_xy = map_position_x[position_y]
                    if map_position_xy=="G" or  map_position_xy=="U" :
                        return None
                    else:
                        if "Potato" in seed_selected:
                            seed_selected_m = PotatoPlant()
                        elif "Kale" in seed_selected:
                            seed_selected_m = KalePlant()
                        elif "Berry" in seed_selected:
                            seed_selected_m = BerryPlant()

                inventory_list=self._player.get_inventory()
                if inventory_list.get(seed_selected) is None:
                    return
                self._model.add_plant(position, seed_selected_m)
                self._player.remove_item((seed_selected,1))

        if event.keysym=="h":
            position=self._player.get_position()
            plants=self._model.get_plants()
            if plants.get(position) is None:

                return
            else:

                locate=plants.get(position)
                if locate.can_harvest():

                    harvest= locate.harvest()
                    self._model.harvest_plant(position)
                    self._player.add_item(harvest)

        if event.keysym == "r":
            self._model.remove_plant(position)

        if event.keysym =="t":
            position = self._player.get_position()
            pos_x,pos_y=position
            map_position = self._model.get_map()
            map_position_xy = map_position[pos_x][pos_y]
            if map_position_xy == "U":
                self._model.till_soil((pos_x,pos_y))


        if event.keysym == "u":
            position = self._player.get_position()
            pos_x,pos_y=position
            plants = self._model.get_plants()
            map_position = self._model.get_map()
            map_position_xy = map_position[pos_x][pos_y]
            if map_position_xy == "S":
                self._model.untill_soil((pos_x,pos_y))

        self.redraw()

    def select_item(self, item_name: str)-> None:
        """
        The callback to be given to each ItemView for item selection. This method should set the
        selected item to be item name and then redraw the view.
        Args:
            item_name: click and select
        """
        self.redraw()
        plant_amount=self._player.get_inventory().get(item_name)
        if plant_amount is not None:
            if plant_amount > 0:
                self._player.select_item(item_name)
        self.redraw()

    def buy_item(self, item_name: str) -> None:
        """
        The callback to be given to each ItemView for buying items.
        Args:
            item_name: the one you click its buy button
        Returns: redrew the canva
        """
        self._player.buy(item_name,int(BUY_PRICES.get(item_name)))
        self.redraw()

    def sell_item(self, item_name: str) -> None:
        """
         The callback to be given to each ItemView for selling items.
        Args:
            item_name: the one you click its sell button
        Returns: redrew the canva
        """
        self._player.sell(item_name,int(SELL_PRICES.get(item_name)))
        self.redraw()

    def open_file(self):
        """
        open the map file and recreate it
        Returns:new tkinker
        """
        filename = filedialog.askopenfilename()
        if filename ==" ":
            return
        self._farmview.clear_cache()
        self._model=FarmModel(filename)
        dimension=self._model.get_dimensions()
        self._farmview.set_dimensions(dimension)
        self._player=self._model.get_player()
        self._inventory=self._player.get_inventory()
        self.redraw()


    def quit_game(self):
        """
        quit and destory tk
        """
        self._master.destroy()
        self._master.quit()



def main() -> None:
    root = tk.Tk()
    map_file = 'maps/map1.txt'
    play_game(root, map_file)



if __name__ == '__main__':
    main()
