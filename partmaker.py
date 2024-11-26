import os
import random


def generate_parts(start, end, parts):
    # Calculate the number of IDs in each part
    ids_per_part = (end - start + 1) // parts
    remainder = (end - start + 1) % parts

    part_start = start
    for i in range(parts):
        part_end = part_start + ids_per_part - 1 + (1 if i < remainder else 0)
        yield part_start, part_end
        part_start = part_end + 1


if __name__ == '__main__':
    start = 1
    end = 1500
    parts = 4
    sessions = [ss for ss in os.listdir(os.getcwd()) if '.json' in ss]

    for part_number, (part_start, part_end) in enumerate(generate_parts(start, end, parts), 1):
        print(f'start cmd /k python messho_seleniumbase_multy_session.py {part_start} {part_end} {part_number}\n timeout 6')
