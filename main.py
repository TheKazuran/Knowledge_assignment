"""
Game that is a basic simulation of a farm by being able to plant, water and harvest crops, feed and herd animals.
How to play:
Use left mouse button to preform actions:
    plant or buy crops and animals
    Water, feed, harvest or pet animals
    remove dead crops or animals
Use the right mouse button to remove crops or sell living animals
Use the scroll wheel to scroll through the options to buy crops or animals. Click the scroll wheel to switch between the
animal or crop list.

"""

# import build in
from math import floor

# import other
import pygame

# import own
import farm_sql


__author__ = 'Kenrick Stadt'
__email__ = 'k.stadt@outlook.com'
__credits__ = ["Kenrick Stadt"]


# from pygame.locals import *


class Game:
    def __init__(self):
        """
        Main class to run the farmsim game
        """
        self._running = True
        self._screen = None
        self.SIZE = self.WIDTH, self.HEIGHT = 610, 400
        self._font = None
        self._FONT_SIZE = 15
        self.FPS = 60
        self.F_TIMER = self.FPS * 1.5 + 1
        """
        self._running: (boolean) used to check if the game should run or not
        self._screen: (None) used to create the display screen
        self.SIZE: (tuple) used as a reference to the pixel width and length of the screen
        self.WIDTH: (integer) reference to the pixel width of the screen
        self.HEIGHT: (integer) reference to the pixel height of the screen
        self.font: (None) used to set the font type used in the labels
        self._FONT_SIZE: (integer) the font size for the font 
        self.FPS: (integer) set to the frames per second the games should run on
        self.F_TIMER: (integer) used to determine how long certain labels will be shown
        """

        self._buy_type = None
        self._buy_list = None
        self._buy = None
        """
        self._buy_type: (None) will become a string to reference which list is selected
        self._buy_list: (None) will become a list of tuples 
        self._buy: (None) will become a tuple which is used to 'buy' 
        """

        self._COLUMNS = 4
        self._ROWS = 3
        self._mouse_pos = None
        self._money_frame_timer = 0
        """
        self._COLUMNS: (integer) reference to the number of columns if the farm field
        self._ROWS: (integer) reference to the number of rows in the farm field
        self._mouse_pos: (None) used to reference at what position the mouse is at
        """

        self._money = 1000
        self._money_gained = 0
        self._mtr = []
        self._day = 0
        """
        self._money: (integer) the amount of cash in the bank account
        self._money_gained: (integer) the amount of money gained or lost in the latest transaction
        self._mtr: (list) empty list that will be filled to reference the farm tiles
        self._day: (integer) day tracker
        """

    def on_init(self):
        pygame.init()
        self._screen = pygame.display.set_mode(self.SIZE, pygame.HWSURFACE)
        self._font = pygame.font.SysFont('Arial', self._FONT_SIZE)
        for i in range(self._ROWS):
            self._mtr.append([None] * self._COLUMNS)
        self._get_buy_list()
        self._running = True

    def on_event(self, event):
        """
        Function that executes commands depending on the input (events) from the player, e.g. mouse clicks and button
        presses.
        currently implemented:
            Left mouse button clicks: preform actions;
            Right mouse button: clear tile and sell animals;
            Scroll wheel: scroll through and switch buy_list;
            Mouse motion: detect mouse position for highlighting;

        Key presses w, a, s and d plus key_up, key_left, key_down and key_right are reserved for further use.
        :param event: an event from pygame.event.get()
        """
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                # move up
                pass
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                # move left
                pass
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                # move down
                pass
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                # move right
                pass

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # left mouse button
                self.det_mouse_pos(event.pos)
                self._action_execute()

            elif event.button == 3:
                # right mouse button
                self.det_mouse_pos(event.pos)
                self._clear_sell()

            elif event.button == 2:
                # middle mouse button
                self._switch_buy_list()

            elif event.button == 4:
                # scroll up
                self._buy_list_scroll(event.button)

            elif event.button == 5:
                # scroll down
                self._buy_list_scroll(event.button)

        elif event.type == pygame.MOUSEMOTION:
            self.det_mouse_pos(event.pos)

    def on_loop(self):
        """
        Function to execute actions that should be preformed each loop iteration.
        If a frame timer is active reduce the number of frames by 1
        """
        if self._money_frame_timer > 0:
            self._money_frame_timer -= 1

    def on_render(self):
        """
        Used to put labels on to the screen and highlight the areas where the mouse is hovering.
        """
        self._screen.fill((0, 0, 0))

        self._highlight()

        label_money = self._font.render('Money: ' + str(self._money), True, (255, 255, 0))
        self._screen.blit(label_money, (10, self.HEIGHT - self._FONT_SIZE - 10))

        label_end_day = self._font.render('End the _day', True, (255, 255, 255))
        self._screen.blit(label_end_day, (self.WIDTH - 75, self.HEIGHT - self._FONT_SIZE - 10))

        label_buy = self._font.render('Buy: ' + self._buy[0] + ' (' + str(self._buy[1]) + ')', True, (255, 255, 255))
        self._screen.blit(label_buy, (floor(self.WIDTH / 3), self.HEIGHT - self._FONT_SIZE - 10))

        label_day = self._font.render('Day: ' + str(self._day), True, (255, 255, 255))
        self._screen.blit(label_day, (floor(self.WIDTH / 2), self._FONT_SIZE))

        if self._money_frame_timer:
            if self._money_gained < 0:
                text = ' - ' + str(-self._money_gained)
                rgb = (255, 0, 0)
            else:
                text = ' + ' + str(self._money_gained)
                rgb = (255, 255, 0)
            label_gained = self._font.render(text, True, rgb)
            self._screen.blit(label_gained, (50, self.HEIGHT - self._FONT_SIZE * 3))

        self.set_labels()

        pygame.display.update()

    def on_cleanup(self):
        """
        Function to quit all PyGame modules
        """
        pygame.quit()

    def on_execute(self):
        """
        Initializes the game and is the main loop wherein the game runs until game is shutdown. On each iteration the
        events will be checked and the corresponding actions taken. The on_loop actions will be executed to finally
        update the screen.
        An internal PyGame clock is used to set the game to 60 frames per second
        """
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            pygame.time.Clock().tick(self.FPS)

        self.on_cleanup()

    def det_mouse_pos(self, pos):
        """
        When called will detect the mouse position, clicked or moving, by evaluating the x and y coordinates.
        If the position is over a 'button' (text label on the screen) such as save it will give this setting to the
        _mouse_pos variable.
        If the mouse position is on a farm tile it will calculate which farm tile it is in the matrix and will set the
        _mouse_pos variable to a tuple with the column and row numbers.

        :param pos : (tuple) - (x,y) coordinates from pygame.event.pos
        """
        x_cor = pos[0]
        y_cor = pos[1]
        if 0 < x_cor < 35 and 0 < y_cor < 20:
            self._mouse_pos = 'save'

        elif (self.WIDTH - 115) < x_cor and (self.HEIGHT - self._FONT_SIZE - 20) < y_cor:
            self._mouse_pos = 'end _day'

        elif 25 < x_cor < (150 * self._COLUMNS) and 25 < y_cor < (120 * self._ROWS):
            eq1 = floor((x_cor - 25) / 150)
            eq2 = floor((y_cor - 25) / 120)
            self._mouse_pos = (eq1, eq2)

        else:
            self._mouse_pos = None

    def _get_buy_list(self):
        """
        When called will import the name and price from the corresponding type table in the sql database.
        """
        if self._buy_type is None:
            self._buy_type = 'vegetables'

        connection = farm_sql.create_connection('farmsim.sql')
        query = """SELECT KIND, price FROM """ + self._buy_type

        self._buy_list = farm_sql.execute_read_query(connection, query, feedback=True)
        self._buy = self._buy_list[0]
        connection.close()

    def _buy_list_scroll(self, up_down):
        """
        It will set the _buy variable to the previous or next item in the _buy_list depending on the input.

        todo:Remove the for loop and use an index which is added / subtracted. The self._buy will become obsolete
            and parts of the code need to be changed

        :param up_down: (integer) button clicked value from pygame.event.button
        """
        for ind, i in enumerate(self._buy_list):
            if i[0] == self._buy[0]:
                if up_down == 4:
                    ind += 1
                    if ind >= len(self._buy_list):
                        self._buy = self._buy_list[0]
                    else:
                        self._buy = self._buy_list[ind]
                else:
                    ind -= 1
                    self._buy = self._buy_list[ind]
                break

    def _switch_buy_list(self):
        """
        When called switches the buy list form animal to vegetable or the other way around and imports the corresponding
        list.
        """
        if self._buy_type == 'vegetables':
            self._buy_type = 'animals'
        else:
            self._buy_type = 'vegetables'

        self._get_buy_list()

    def _get_label_text(self, coordinates):
        """
        When called will get determine text for the farm tile labels. The main label will get the name of the KIND of
        the animal or vegetable if any. The sublabel text is given certain attributes from these classes e.g. watered
        fed or that its product is ready to be collected.

        :param coordinates: (tuple) - (column, row)  for the tile in the matrix of whom the labels are being determined
        :return:
            name: (string) with name of animal, vegetable or set to soil;
            KIND: (string) with the class type or clear;
            sub_text: (string) with the subtext

        """
        # y = [5 + 150 * y, 5 + 150 * (y + 1)]
        # x = [5 + 120 * x, 5 + 120 * (x + 1)]
        x = coordinates[0]
        y = coordinates[1]
        sub_text = ''

        if isinstance(self._mtr[y][x], Vegetable):
            name = self._mtr[y][x].KIND
            kind = 'Vegetable'

            if self._mtr[y][x].dead:
                sub_text = 'Dead'
            elif self._mtr[y][x].days_grown == 0:
                sub_text = 'Planted'
            elif self._mtr[y][x].harvest:
                sub_text = 'Harvest'
            elif self._mtr[y][x].days_grown:
                sub_text = 'Growing'

            if self._mtr[y][x].watered:
                sub_text += ', watered'

        elif isinstance(self._mtr[y][x], Animal):
            name = self._mtr[y][x].KIND
            kind = 'Animal'
            if self._mtr[y][x].dead:
                sub_text = 'Dead'
            else:
                if self._mtr[y][x].harvest and self._mtr[y][x].adult:
                    sub_text = 'Produce'
                elif self._mtr[y][x].adult:
                    sub_text = 'Adult'
                else:
                    sub_text = 'Youngster'

                if self._mtr[y][x].fed:
                    sub_text += ' Fed'

                if self._mtr[y][x].petted:
                    sub_text += ' Petted'

        else:
            name = 'Soil'
            kind = 'clear'
            sub_text = None

        return name, kind, sub_text

    def set_labels(self):
        """
        When called creates the labels for each of the farm tiles. Colors depend on the type and if the animal or crop
        on that tile is dead or not.
        """
        for i in range(self._ROWS):
            for j in range(self._COLUMNS):
                name, kind, stage = self._get_label_text((j, i))
                x = 75 + 150 * j
                y = 50 + 120 * i

                if not stage == 'Dead':
                    if kind == 'Vegetable':
                        rgb = (0, 205, 0)

                    elif kind == 'Animal':
                        rgb = (204, 0, 0)

                    else:
                        rgb = (255, 128, 0)
                else:
                    rgb = (145, 58, 4)

                label = self._font.render(name, True, rgb)
                self._screen.blit(label, (x, y))

                if stage:
                    label = self._font.render(stage, True, rgb)
                    self._screen.blit(label, (x, y + 5 + self._FONT_SIZE))

    def _highlight(self):
        """
        Function that draws a highlighting rectangle on a clickable area where the mouse is positioned.
        """
        rgb = (45, 163, 186)
        rect = None
        if self._mouse_pos == 'save':
            pass
        elif self._mouse_pos == 'end _day':
            rect = (self.WIDTH - 115,
                    self.HEIGHT - self._FONT_SIZE - 20,
                    115,
                    self._FONT_SIZE + 20)
        elif type(self._mouse_pos) == tuple:
            rect = (25 + 150 * self._mouse_pos[0],
                    25 + 120 * self._mouse_pos[1],
                    150,
                    120)

        if rect:
            pygame.draw.rect(self._screen, rgb, rect)

    def _action_execute(self):
        """"
        Attribute that depending on the mouse location performs different actions when called.
        If the mouse is clicked in an area without any actions (None) it passes and does not perform any
        actions.
        If the end _day button is clicked it will run the end of _day functions.
        If the mouse has been clicked in the area of the farm performs actions depending on what is on the local area.
            For clear areas perform _buy
            For Animals perform _animal_action
            For Vegetables perform _vegetable_action

        To do:
            implement save
            implement load
        """
        if self._mouse_pos is None:
            pass

        elif self._mouse_pos == 'end _day':
            self.end_day()

        elif self._mouse_pos == 'save':
            # reserved for save function
            pass

        elif self._mouse_pos == 'load':
            # reserved for load function
            pass

        elif type(self._mouse_pos) == tuple:
            pos = self._mouse_pos

            if self._mtr[pos[1]][pos[0]] is None:
                self._buy_crop_animal()

            elif isinstance(self._mtr[pos[1]][pos[0]], Vegetable):
                self._action_vegetable(pos)

            elif isinstance(self._mtr[pos[1]][pos[0]], Animal):
                self._action_animal(pos)

    def _action_vegetable(self, pos):
        """
        When called checks if the vegetable on the given position is dead, then determines if it can be harvested and
        harvests the crop. On the next call for the same position if the crop has not been watered it will water it.

        When the crop is harvested a frame timer is set to display how much money was add to the bank account.

        :param pos (tuple): tuple of (x,y) for the matrix '_mtr' location as given by det_mouse_pos
        """
        if self._mtr[pos[1]][pos[0]].dead:
            self._clear_sell()

        elif self._mtr[pos[1]][pos[0]].harvest:
            self._mtr[pos[1]][pos[0]].harvest_crop()
            self._money_gained = self._mtr[pos[1]][pos[0]].value
            self._money += self._mtr[pos[1]][pos[0]].value
            self._money_frame_timer = self.F_TIMER

        elif not self._mtr[pos[1]][pos[0]].watered:
            self._mtr[pos[1]][pos[0]].water()

    def _action_animal(self, pos):
        """
        When called will check if the animal is dead and clear the tile if so. If the animal has a product than can be
        collected will collect it and add its value to the bank account. Then if the animal has not been fed feeds it
        to finally give some attention the the animal by petting it if not already done that day.

        When the produce is gathered a frame timer is set to display how much money was add to the bank account.

        Note: The product first needs to be collected before the animal can be fed. After feeding the animal can be
        petted. These actions will be performed individually

        :param pos (tuple): tuple of (x,y) for the matrix '_mtr' location as given by det_mouse_pos
        """
        if self._mtr[pos[1]][pos[0]].dead:
            self._clear_sell()

        elif self._mtr[pos[1]][pos[0]].harvest:
            self._money_gained = self._mtr[pos[1]][pos[0]].get_produce()
            self._money += self._money_gained
            self._money_frame_timer = self.F_TIMER

        elif not self._mtr[pos[1]][pos[0]].fed:
            self._mtr[pos[1]][pos[0]].feed()

        elif not self._mtr[pos[1]][pos[0]].petted:
            self._mtr[pos[1]][pos[0]].pet()

    def _clear_sell(self):
        """
        When called will check if the tile selected is a living animal and preform its sell action then will clear the
        tile regardless of type.
        When an animal is sold will set a frame timer to display how much money was add to the bank account.
        """
        if isinstance(self._mtr[self._mouse_pos[1]][self._mouse_pos[0]], Animal) and not \
                self._mtr[self._mouse_pos[1]][self._mouse_pos[0]].dead:
            self._money_gained = self._mtr[self._mouse_pos[1]][self._mouse_pos[0]].sell()
            self._money += self._money_gained
            self._money_frame_timer = 2 * self.FPS + 1

        self._mtr[self._mouse_pos[1]][self._mouse_pos[0]] = None

    def _buy_crop_animal(self):
        """
        When called will buy, and fill, an animal or vegetable for the current active tile. The detection to buy an
        animal or vegetable is done by the _buy_type variable. After setting the newly bought to a tile it subtracts
        its buy price from the bank account. Will only preform if the bank account supports the purchase.
        """
        if self._money >= self._buy[1]:
            if self._buy_type == 'vegetables':
                self._mtr[self._mouse_pos[1]][self._mouse_pos[0]] = Vegetable(kind=self._buy[0])
            else:
                self._mtr[self._mouse_pos[1]][self._mouse_pos[0]] = Animal(kind=self._buy[0])
            self._money_gained = -self._buy[1]
            self._money -= self._buy[1]
            self._money_frame_timer = self.F_TIMER

    def end_day(self):
        """
        When called will end the _day an for each tile preform its end_day function.
        """
        self._day += 1
        for rows in self._mtr:
            for i in rows:
                if i:
                    i.end_day()


class Vegetable:
    def __init__(self, kind='Wheat'):
        """
        Class for crops in the farmsim game

        todo: rework how quality works
        todo: rework how watering works --> not watering kills the crop
        todo: implement some sort of fertilizer effect
        todo: implement semi random yield

        :param kind: (str) containing the name of the crop
        """
        self.KIND = kind
        self._days_to_grow = None
        self._basic_val = None
        self._produce = None
        self._multi_grow = None

        """
        self.KIND: (string) name fo the type of crop
        self._days_to_gro: (None) will become an integer with the number of days untill the crop can be harvested
        self._basic_val: (None) will become an integer with the basic value of the crop
        self._produce: (None) will become an integer of the maximum crops harvested from the plant per harvest 
        self._multi_grow: (None) will become an integer with the amount of times the crop can be harvested
        """

        self._quality = 1.0
        self.days_grown = 0
        self.dead = False
        self.watered = False
        self.harvest = False
        self.value = 0
        self._times_grown = 0
        """
        self._quality: (float) determines the quality of the crop
        self.days_grown: (integer) keeps track of how many days the crop has grown
        self.dead: (boolean) determines if the crop is dead or not
        self.harvest: (boolean) determines if the crop can be harvested or not
        self.value: (integer) used to set the value of the harvested crop
        self._times_grown: (integer) determines how many times the crop has been harvested
        """

        self._get_sql_data()

    def _get_sql_data(self):
        """
        Gets the SQL data from the vegetable table corresponding to the type of crop and sets the corresponding
        variables
        """
        query = """SELECT * FROM vegetables WHERE KIND=?"""
        tup = (self.KIND,)
        conn = farm_sql.create_connection('farmsim.sql')
        data = farm_sql.execute_read_query_v2(conn, query, tup)

        self._days_to_grow = data[0][2]
        self._basic_val = data[0][3]
        self._produce = data[0][4]
        self._multi_grow = data[0][5]

        conn.close()

    def end_day(self):
        """
        Checks if the age of the crop has extended beyond the maximum grow age to kill it, if not, will grow the crop
        and checks if the crop can be harvested and if the crop has been watered to increase its quality
        """
        if self.days_grown >= self._days_to_grow:
            self.dead = True
        else:
            self.days_grown += 1
            if self.days_grown == self._days_to_grow:
                self.harvest = True
            if self.watered:
                self._quality += 1 / self._days_to_grow
                self.watered = False

    def water(self):
        """"
        Nothing special, just waters the crop
        """
        self.watered = True

    def harvest_crop(self):
        """
        If the crop can be harvested will add to the times the crop has grown then determines the value of the crop's
        yield. Resets the age of the crop if has multiple grow cycles otherwise kills the crop.
        """
        if self.harvest:
            self._times_grown += 1
            self.value = floor(self._produce * self._basic_val * self._quality)
            if self._times_grown < self._multi_grow:
                self.days_grown = 1
                self.harvest = False
            else:
                self.dead = True


class Animal:
    def __init__(self, kind='Cow'):
        """
        Class for animals in the farm sim game

        todo: revise the hunger mechanic

        :param kind: (str) with the name of the type of animal
        """
        self.KIND = kind
        self._AGE_ADULT = None
        self._AGE_MAX = None
        self._BASE_VAL_ANIM = None
        self._BASE_VAL_PROD = None
        self._DAYS_TO_PROD = None
        """
        self.KIND: (str) with the name of the type of animal used to get all the animals data
        
        self._AGE_ADULT: (None) will become an integer with the age when the animal is considered an adult in days used
        to determine if the adult can produce 
        
        self._AGE_MAX: (None) will become an integer with tha maximum age of the animal in days used to determine when
        the animal dies of old age and the animals value
        
        self._BASE_VAL_ANIM: (None) will become an integer with the base value of the animal (1/4th of the price) used
        to determine the animals value when sold
        
        self._BASE_VAL_PROD: (None) will become an integer with the base value of the product the animal will produce
        used to determine the animals product value
        
        self._DAYS_TO_PROD: (none) will become an integer that determines production speed used to determine if the 
        animal has a product ready to be collected
        """

        self._days_since_product = 0
        self._happy = 0
        self.petted = False
        self.age = 0
        self.fed = False
        self._hunger = 0
        self.dead = False
        self.harvest = False
        self.adult = False
        """
        self._days_since_product: (integer) with the days since the animal last produced
        self._happy: (integer) the happiness of the animal 
        self.petted: (boolean) did you give the animal attention? 
        self.age: (integer) the age of the animal 
        self.fed: (boolean) did you feed your animal? 
        self._hunger: (integer) used to determine if the animal is hungry or not
        self.dead: (boolean) used to mark if the animal died or not
        self.harvest: (boolean) used to mark if the animal has a product to gather
        self.adult: (boolean) used to check if the animal is an adult or not
        """

        self._get_sql_data()

    def _get_sql_data(self):
        """
        Gets the SQL data from the animals table corresponding to the type of animal and sets the corresponding
        variables
        """
        query = """SELECT * FROM animals WHERE KIND=?"""
        tup = (self.KIND,)
        conn = farm_sql.create_connection()
        data = farm_sql.execute_read_query_v2(conn, query, tup)

        self._AGE_ADULT = data[0][2]
        self._AGE_MAX = data[0][3]
        self._BASE_VAL_ANIM = floor(data[0][1] / 4)
        self._BASE_VAL_PROD = data[0][5]
        self._DAYS_TO_PROD = data[0][4]

        conn.close()

    def feed(self):
        """
        You are a nice person if you feed your animal which is what this function does
        """
        self.fed = True

    def pet(self):
        """
        You are even nicer of you give the animal some attention by petting it!
        """
        self.petted = True

    def get_produce(self):
        """
        If the animal is an adult and has produced its product, it can be harvested. Its value is calculated by the
        happiness of the animal and the product's base value
        :return: prod_val (integer) the value of the gathered product
        """
        if self.harvest:
            self.harvest = False
            if self._happy < 25:
                prod_val = self._BASE_VAL_PROD
            else:
                prod_val = floor(self._happy / 25 * self._BASE_VAL_PROD)
        return prod_val

    def sell(self):
        """
        Getting rid of your animal by selling it returns some of its costs. First the animal must be an adult to get
        more value. Then the age up to 1/2 its maximum age will increase its value if the animal is older it will go
        down again. A happy animal is worth more.
        Finally the value of the animal will be rounded down.
        :return: val: (integer) value of the sold animal
        """
        val = self._BASE_VAL_ANIM
        if self.adult:
            if self.age * 2 / (self._AGE_MAX / 2) > 1 and self.age <= (self._AGE_MAX / 2):
                val = val * self.age * 2 / (self._AGE_MAX / 2)

            elif (self._AGE_MAX - self.age) * 2 / (self._AGE_MAX / 2) > 1 and self.age >= (self._AGE_MAX / 2):
                val = val * (self._AGE_MAX - self.age) * 2 / (self._AGE_MAX / 2)

            if self._happy > 50:
                val = val * self._happy / 50

            val = floor(val)

        return val

    def end_day(self):
        """
        Actions that will be done when the attribute is called:
            determine if the animal has been fed, if it is hungry decrease its hunger if not increase the days since
            it produced and set the harvest boolean to true, else increase its hunger, decrease its happiness and
            when starved kill the animal

            if the animal received attention increase its happiness, otherwise decrease it

            increase its age and when its too old it will die
        """
        if self.fed:
            self.fed = False
            if self._hunger < 0:
                self._hunger += 1
            else:
                if self.adult:
                    self._days_since_product += 1
                    if self._days_since_product == self._DAYS_TO_PROD:
                        self.harvest = True
                        self._days_since_product = 0
        else:
            self._hunger -= 1
            self._happy = -10
            if self._hunger == -3:
                self.dead = True

        if self.petted:
            self.petted = False
            if self._happy <= 85:
                self._happy += 15
            else:
                self._happy = 100
        else:
            self._happy -= 5

        self.age += 1
        if not self.adult:
            if self.age >= self._AGE_ADULT:
                self.adult = True
        if self.age >= self._AGE_MAX:
            self.dead = True


if __name__ == '__main__':
    theGame = Game()
    theGame.on_execute()

