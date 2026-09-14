"""

Author:  Adam England
Date written: 02/20/25
Assignment:   Final Project
Short Desc:   Design a functioning GUI Application


"""
import tkinter as tk
import tkinter.messagebox

def mmWindow():
    '''
    Creates and displays the main menu window for the Golf Trainer application.
    '''
    #Sets up the window and the color
    Window = tk.Tk()
    Window.geometry('750x500')
    Frame = tk.Frame(Window, bg = "lime green")
    Frame.place(relwidth = 1, relheight = 1)
    #Changes the title to Golf trainer
    Window.title("Golf Trainer")

    #Creates the label for the first Question 
    Que1 = tk.Label(Window, text = "ARE YOU ON THE GREEN?", font = ("Times",12), fg = "white", bg = "green"
                    , padx = 75, pady = 25)
    Que1.place(x=100, y=175)
    
    #creats an exit button to close the program
    exit_button = tk.Button(Window, text = "EXIT", height = 2, width = 8, font = ("Times",12)
                            ,fg = "white", bg = "green",command = lambda: Exit(Window))
    exit_button.place(x = 655, y = 14)
   



    #Creates a button that allows the user to click Yes
    Yes_button = tk.Button(Window, text = "YES", height = 5, width = 15, font = ("Times",12)
                           ,fg = "white", bg = "green", command = lambda: Off_green(Window))
    Yes_button.place(x=100, y = 275)
    #Creates a button that allows the user to click No
    No_button = tk.Button(Window, text = "NO", height = 5, width = 15, font = ("Times",12)
                          ,fg = "white", bg = "green", command = lambda: On_green(Window))
    No_button.place(x=300, y = 275)

    #places an image onto the window 
    image = tk.PhotoImage(file=r"Photos\PuttingGreen.png")
    smaller_image = image.subsample(10,7)
    label = tk.Label(Frame, image=smaller_image)
    label.image = smaller_image
    label.place(x=500,y=150)

#Function to deal with the "Yes" button
def On_green(current_window):
    '''
    Handles the case where the user is on the green, transitioning to the distance input screen.
    '''
    current_window.destroy()
    Distance("male")
# Function to deal with the "No" button
def Off_green(current_window):
    '''
    Handles the case where the user is off the green, providing a putting recommendation.
    '''
    current_window.destroy()
    Recommendation()
#Function to close the application
def Exit(current_window):
    '''
    Closes the current window and exits the application.
    '''
    current_window.destroy()
    
#Calls the first window  
mmWindow()                
#Function to get the distance to the green from the user 
def Distance(gender):
    '''
    Creates and displays the window for the user to input the distance from the green.
    '''
    Window = tk.Tk()
    Window.geometry('750x500')
    Frame = tk.Frame(Window, bg = "lime green")
    Frame.place(relwidth = 1, relheight = 1)

    Window.title('Distance')

    #Creates the box behind the input
    box = tk.Label(Window, text = "", font = ("Times",12), fg = "white", bg = "green"
                    , padx = 170, pady = 25)
    box.place(x=100, y=175)

    #Creates a label for the question
    Que1 = tk.Label(Window, text = "ENTER THE DISTANCE FROM GREEN", font = ("Times",12), fg = "white", bg = "green"
                    , padx = 170, pady = 25)
    Que1.place(x=100, y=75)
    #Creates the entry box to get the distance from the user 
    entry = tk.Entry(Window, width = 25)
    entry.place(x = 200, y = 200)
    
    
    #creats an exit button to close the program
    exit_button = tk.Button(Window, text = "EXIT", height = 2, width = 8, font = ("Times",12)
                            ,fg = "white", bg = "green",command = lambda: Exit(Window))
    exit_button.place(x = 655, y = 14)
    #Creates a button to allow the user to go back a page
    back_button = tk.Button(Window, text = "BACK", height = 2, width = 8, font = ("Times",12),
                            fg = "white", bg = "green",command = lambda: Back(Window))
    back_button.place(x = 10, y = 14)
                            
   




    male_button = tk.Button(Window, text = "MALE", height = 5, width = 15, font = ("Times",12)
                           ,fg = "white", bg = "green", command = lambda: Rec(Window, entry.get(), "male"))
    male_button.place(x=100, y = 275)

    female_button = tk.Button(Window, text = "FEMALE", height = 5, width = 15, font = ("Times",12)
                          ,fg = "white", bg = "green",command = lambda: Rec(Window,entry.get(), "female"))
    female_button.place(x=300, y = 275)


    image = tk.PhotoImage(file=r"Photos\PuttingGreen.png")
    smaller_image = image.subsample(10,7)
    label = tk.Label(Frame, image=smaller_image)
    label.image = smaller_image
    label.place(x=502,y=150)
#Function to get recommendation based on distance and gender
def Rec(current_window, distance, gender):
    '''
    Validates distance input and calls the Recommendation function with the distance and gender.
    '''
    if not distance: # check if the entry is empty
        tk.messagebox.showerror("Error", "Please enter a distance.")
        current_window.destroy()
        Distance(gender)
        return

    try:
        distance_value = float(distance)
        current_window.destroy()
        Recommendation(distance_value, gender)
    except ValueError:
        tk.messagebox.showerror("Error", "Invalid distance input. Please enter a number.")
        current_window.destroy()
        Distance(gender)
        
#Function to go back to the main menu
def Back(current_window):
    '''
    Returns the user to the main menu window.
    '''
    current_window.destroy()
    mmWindow()
#Function to exit the application
def Exit(current_window):
    '''
    Closes the current window and exits the application.
    '''
    current_window.destroy()
    

    
    


    

#Function to display the Recommendation
def Recommendation(distance = None, gender = None):
    '''
    Provides a golf club recommendation based on the provided distance and gender.
    If no distance is provided, it recommends a putter.
    '''
    Window = tk.Tk()
    Window.geometry('750x500')
    Frame = tk.Frame(Window, bg = "lime green")
    Frame.place(relwidth = 1, relheight = 1)
    #If else statement to decide which club to use based off the distanced entered by the user
    Window.title("Recommendation")
    #Distance for male users
    if distance is not None and gender == "male":
        if distance <= 100:
            recommendation_text = "I'd recommend using a Pitching Wedge"
        elif distance <= 115 and distance > 100:
            recommendation_text = "I'd recommend using a 9 Iron"
        elif distance <= 130 and distance > 115:
            recommendation_text = "I'd recommend using a 8 Iron"
        elif distance <= 140 and distance > 130:
            recommendation_text = "I'd recommend using a 7 Iron"
        elif distance <= 145 and distance > 140:
            recommendation_text = "I'd recommend using a 6 Iron"
        elif distance <= 155 and distance >145:
            recommendation_text = "I'd recommend using a 5 Iron"
        elif distance <= 160 and distance >155:
            recommendation_text = "I'd recommend using a 4 Iron"
        elif distance <= 170 and distance > 160:
            recommendation_text = "I'd recommend using a 3 Iron"
        elif distance <= 180 and distance > 170:
            recommendation_text = "I'd recommend using a 2 Iron or hybrid"
        elif distance <= 195 and distance > 180:
            recommendation_text = "I'd recommend using a 5 Wood"
        elif distance <= 210 and distance >195:
            recommendation_text = "I'd recommend using a 3 Wood"
        else:
            recommendation_text = "I'd recommend using a Driver"
    #Distance for female users
    elif distance is not None and gender == "female":
        if distance <= 60:
            recommendation_text = "I'd recommend using a Pitching Wedge"
        elif distance <= 70 and distance > 60:
            recommendation_text = "I'd recommend using a 9 Iron"
        elif distance <= 80 and distance > 70:
            recommendation_text = "I'd recommend using a 8 Iron"
        elif distance <= 90 and distance > 80:
            recommendation_text = "I'd recommend using a 7 Iron"
        elif distance <= 100 and distance > 90:
            recommendation_text = "I'd recommend using a 6 Iron"
        elif distance <= 110 and distance >100:
            recommendation_text = "I'd recommend using a 5 Iron"
        elif distance <= 120 and distance >110:
            recommendation_text = "I'd recommend using a 4 Iron"
        elif distance <= 140 and distance > 120:
            recommendation_text = "I'd recommend using a 5 Wood or hybrid"
        elif distance <= 160 and distance >140:
            recommendation_text = "I'd recommend using a 3 Wood"
        else:
            recommendation_text = "I'd recommend using a Driver"
    else:
        recommendation_text = "I'd recommend using a Putter"
        

        
        
        
        
    #Creates a label to print the recommeneded club to use
    Que1 = tk.Label(Window, text = recommendation_text, font = ("Times",12), fg = "white", bg = "green"
                    , padx = 60, pady = 25)
    Que1.place(x=100, y=175)
    
    #creats an exit button to close the program
    exit_button = tk.Button(Window, text = "EXIT", height = 2, width = 8, font = ("Times",12)
                            ,fg = "white", bg = "green",command = lambda: Exit(Window))
    exit_button.place(x = 655, y = 14)
    #Creates a button to allow the user to go back a page
    back_button = tk.Button(Window, text = "BACK", height = 2, width = 8, font = ("Times",12),
                            fg = "white", bg = "green",command = lambda: Back(Window))
    back_button.place(x = 10, y = 14)
   




   

    #Grabs the image from the folder and prints it on the window
    image = tk.PhotoImage(file=r"Photos/clubs.png")
    smaller_image = image.subsample(10,7)
    label = tk.Label(Frame, image=smaller_image)
    label.image = smaller_image
    label.place(x=500,y=150)

#Function to go back to the main menu
def Back(current_window):
    '''
    Returns the user to the main menu window.
    '''
    current_window.destroy()
    mmWindow()
#Function to exit the application
def Exit(current_window):
    '''
    Closes the current window and exits the application.
    '''
    current_window.destroy()





    



    



       
