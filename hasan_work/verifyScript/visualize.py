import rasterio
import matplotlib.pyplot as plt
import os
import argparse

index_file = "index.txt"
datasetLen = 10

def get_current_index():
    if os.path.exists(index_file):
        with open(index_file, 'r') as f:
            return int(f.read().strip())
    return 0

def save_current_index(i):
    with open(index_file, 'w') as f:
        f.write(str(i))

def visualizeData(dataIndex):
    # find way to access data from dataIndex
    band = dataset.read(1)
    plt.imshow(band, cmap='gray')
    plt.colorbar(label='Elevation')
    plt.title('Elevation Data')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()

    notData = dataset.nodata

    validData = band != notData
    print("Total area: ", validData.sum() * 2)

    return 0

def next():
    index = get_current_index()
    index += 1 % datasetLen
    save_current_index(index)
    return 0

def prev():
    index = get_current_index()
    index -= 1
    if(index < 0):
        index = datasetLen - 1
    save_current_index(index)
    return 0

def accept():
    pass

def delete():
    pass


def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--action', choices=['next', 'previous', 'delete', 'accept', 'visualize'], required=True)

    choice = argParser.parse_args()

    if choice.action == 'next':
        next()
        return 0
    
    elif choice.action == 'previous':
        prev()
        return 0
    
    elif choice.action == 'accept':
        accept()
        next()
        return 0
    
    elif choice.action == 'delete':
        delete()
        next()
        return 0
    
    elif choice.action == 'visualize':
        index = get_current_index()
        visualizeData(index)
        return 0

if __name__ == '__main__':
    main()