import json
import os

class CageIsFilledError(Exception):
    
    def __init__(self, message="An error occurred"):
        # Call the base class constructor to initialize the message
        super().__init__(message)

class FileIsExists(Exception):

    def __init__(self, message="File is exists!"):
        # Call the base class constructor to initialize the message
        super().__init__(message)


class TicTacToeSession:
    def __init__(self, filename_token, is_new=None, folder_name=''):
        self.filename_token = filename_token
        self.filepath = os.path.join(folder_name, filename_token)

        if is_new:
            data = {
                "data": [

                    [0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0]

                ],
            }

            with open(f'{self.filepath}.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)

        with open(f'{self.filepath}.json', 'r') as json_file:
            # Load (deserialize) the JSON data from the file
            loaded_data = json.load(json_file)

        self.loaded_data = loaded_data
    
    def update(self, x, y, cage_value):

        if self.loaded_data["data"][x][y] != 0:
            raise CageIsFilledError("Cage has been already filled!")
        else:
            self.loaded_data["data"][x][y] = cage_value

    def check_winner(self):
        work_data = self.loaded_data["data"]
        # check for horizontal
        for lst in work_data:
            if lst[0] != 0 and all(i == lst[0] for i in lst):
                return True
        
        #check if vertical
        for pos, value in enumerate(work_data[0]):
            if value != 0 and all(i[pos] == value for i in work_data):
                return True
        
        if work_data[0][0] != 0 and all(work_data[i][i] == work_data[i+1][i+i] for i in range(2)):
            return True
        
        if work_data[0][2] != 0  and work_data[0][2] == work_data[1][1] and work_data[1][1] == work_data[2][0] :
            return True
        
        return False

    def deletegame(self):
        os.remove(f'{self.filepath}.json')

    def commit(self):
        with open(f'{self.filepath}.json', 'w') as json_file:
            json.dump(self.loaded_data, json_file, indent=4)

################################################################################

# session = TicTacToeWSession("filename", is_new=True)
# session.update(0, 0, 2)
# session.update(0, 0, 3)
# print(session.check_winner())
# print(session.loaded_data)
# session.commit()
