import os


def main():
    directory = input("Enter the full path of the directory to scan: ")
    output_file = "file_list.txt"


    if not os.path.isdir(directory):
        print("The provided path is not a valid directory.")
        return


    try:
        with open(output_file, "w", encoding="utf-8") as out_file:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)


                if os.path.isfile(file_path):
                    out_file.write(f"=== {filename} ===\n")
                    try:
                        with open(file_path, "r", encoding="utf-8") as in_file:
                            contents = in_file.read()
                            out_file.write(contents + "\n\n")
                    except Exception as e:
                        out_file.write(f"[Error reading file: {filename}] {str(e)}\n\n")


        print(f"File names and contents written to: {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"Error writing output file: {str(e)}")


if __name__ == "__main__":
    main()