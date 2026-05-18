import os
import sys
from mpi4py import MPI


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()



def brute_force_search(text, pattern):
    return pattern in text



def boyer_moore_search(text, pattern):
    m = len(pattern)
    n = len(text)

    if m == 0:
        return True


    bad_char = {}

    for i in range(m):
        bad_char[pattern[i]] = i

    s = 0

    while s <= n - m:
        j = m - 1

        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1

        if j < 0:
            return True

        else:
            shift = max(1, j - bad_char.get(text[s + j], -1))
            s += shift

    return False



def compute_lps(pattern):
    lps = [0] * len(pattern)

    length = 0
    i = 1

    while i < len(pattern):

        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1

        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    return lps


def kmp_search(text, pattern):
    n = len(text)
    m = len(pattern)

    lps = compute_lps(pattern)

    i = 0
    j = 0

    while i < n:

        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            return True

        elif i < n and pattern[j] != text[i]:

            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return False


def search(text, pattern, algorithm):

    if algorithm == "brute":
        return brute_force_search(text, pattern)

    elif algorithm == "bm":
        return boyer_moore_search(text, pattern)

    elif algorithm == "kmp":
        return kmp_search(text, pattern)

    else:
        raise ValueError(
            "Dostępne algorytmy: brute | bm | kmp"
        )



def main():

    if len(sys.argv) != 4:

        if rank == 0:
            print(
                "Użycie:\n"
                "mpirun -np 4 python main.py <plik> <slowo> <algorytm>\n\n"
                "Algorytmy:\n"
                "brute - brute force\n"
                "bm    - Boyer-Moore\n"
                "kmp   - Knuth-Morris-Pratt"
            )

        sys.exit(1)

    filename = sys.argv[1]
    keyword = sys.argv[2]
    algorithm = sys.argv[3]

    keyword_len = len(keyword)
    file_size = os.path.getsize(filename)

    chunk_size = file_size // size

    start = rank * chunk_size

    if rank == size - 1:
        end = file_size
    else:
        end = start + chunk_size + keyword_len - 1

    end = min(end, file_size)

    found = 0

    BUFFER_SIZE = 4096

    with open(filename, "r", encoding="utf-8", errors="ignore") as f:

        f.seek(start)

        current = start
        overlap = ""

        while current < end:


            global_found = comm.allreduce(found, op=MPI.MAX)

            if global_found == 1:
                break

            read_size = min(BUFFER_SIZE, end - current)

            chunk = f.read(read_size)

            if not chunk:
                break

            data = overlap + chunk

            if search(data, keyword, algorithm):
                found = 1
                break

            overlap = data[-(keyword_len - 1):]

            current += read_size

    result = comm.allreduce(found, op=MPI.MAX)

    if rank == 0:
        print(result)


if __name__ == "__main__":
    main()