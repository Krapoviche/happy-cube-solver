from random import randint

# Function that return the edge of a piece depending on the index asked by the user
# Edge 1 is the one starting at the top left corner
def getArrete(piece, numArrete):
    # Special treatment for the last edge because of it's last bit being actually the first of the piece
    if numArrete == 4 :
        # Making every bit that isn't the 4 lasts
        mask = (1 << 4) - 1

        # Get the first bit
        firstBit = piece >> 15

        # Compute the edge
        res = piece & mask
        return (res << 1) + firstBit

    # For other edges, we create a mask that will keep every bits on the right from the first to the one starting the edge the user is asking for
    masque = (1 << (4 + (4* (4-numArrete)))) - 1

    # Then we apply this mask and shift the result to the right until the end of the edge
    return (piece & masque) >> (4* (4-numArrete) - 1 )

# Function that returns each edge at the same position but horizontally flipped
def flipPiece(edges):
    flippedEdges = []

    # For each edge
    for edge in edges:
        # Start to build the new one
        reversedArrete = ["0","b"]

        # Reverse the edge
        for i in range(len(bin(edge)) -1,1,-1):
            reversedArrete.append(bin(edge)[i])

        # Complete the potentially lost zeros
        while len(reversedArrete) < 5 + 2 :
            reversedArrete.append("0")

        # Translation to an int and append it to flippedEdges
        flippedEdges.append(int("".join(reversedArrete)[2:],2))

    # Switch top and bottom edges (horizontall flip)
    flippedEdges[0],flippedEdges[2] = flippedEdges[2],flippedEdges[0]

    return flippedEdges

# Function that flips a piece directly
def flipPieceInPlace(piece):

    # Getting flipped edges from another function
    flippedEdges = getEdges(piece)[4:]
    flippedPiece  = []

    # For each flipped edge
    for i in flippedEdges:
        # Complete it with zeros (to be sure it's 5 bits long)
        for j in range(len(bin(i).replace("0b","")),5):
            flippedPiece.append("0")

        # Append actual bits of the edge to the piece
        for j in bin(i).replace("0b",""):
            flippedPiece.append(j)

        # Then remove the last one so the next edge will not double it
        flippedPiece.pop()

    return (int("".join(flippedPiece),2))

# Function that returns the rotated piece, doing turns time 1/4 a full rotation
def rotatePiece(piece, turns):
    # Basically, just shift right the piece to move the first edge as much as needed
    shiftedPiece = piece >> (turns*4)

    # Get back the lost bits (overflowed on the right by the shift) using a mask and the original piece
    mask = 2**(turns*4) -1
    lostBits = (piece & mask) << (16 - (turns*4))

    # Return a logical OR of the lost bits shifted on the left and the piece shifted on the right
    return lostBits | shiftedPiece

# This function returns the list of edges of a piece (all of them, standard and flipped)
def getEdges(piece):
    arretes = []

    # Adding edges before flipping
    for i in range(1,5):
        arretes.append(getArrete(piece,i))

    flippedPiece = flipPiece(arretes)

    # Adding edges after flipping
    for i in flippedPiece:
        arretes.append(i)

    return arretes

# Function that returns the compatibility between two edges
def checkEdgeCompatibility(a1, a2):
    # Revert edge2 for the comparison
    a2bin = bin(a2)[2:].zfill(5)  # Convert a2 in a binary chain of 5 bits by filling zeros on the left
    a2 = int(a2bin[::-1], 2)  # Revert the binary chain and read it as an integer (base 2)


    # Check wether the pieces perfectly matches, matches but the first bit (angle), matches but the last bit (angle), matches but both the angles.
    # If it doesn't match perfectly on the angles, we do check that it isn't a 1-1 case which would be the only wrong case.
    if a1 ^ a2 == 0b11111:
        return True
    elif (a1 ^ a2 == 0b1111
        and (a1 >> 4 == 0) and (a2 >> 4 == 0)):
            return True
    elif (a1 ^ a2 == 0b11110
        and (a1 & 1 == 0) and (a2 & 1 == 0)):
            return True
    elif (a1 ^a2 == 0b1110
        and (a1 >> 4 == 0) and (a2 >> 4 == 0)
            and (a1 & 1 == 0) and (a2 & 1 == 0)):
                return True
    return False

# Wrapper that checks the compatibility between an edge and the one following, it only does something with the last side's piece
def checkFollowingEdgeCompatibility(pieceCube,coteCube,piece,cotePiece):
    if(coteCube != 4):
        return True
    return checkEdgeCompatibility(getArrete(pieceCube,coteCube), getArrete(piece,cotePiece))

# Checks the compatibility of three edges, especially the base side angle
def checkAnglesCompatibility(angleBase, angleOldPiece, anglePiece):
    if (angleBase >> 4) + (angleOldPiece & 1) + (anglePiece & 1) == 1:
        return True
    return False

# Wrapper as the first one that checks the following angle of the last side's piece
def edgeBasecheckFollowingAnglesCompatibility(pieceBase, edgeBase, oldPiece, edgeOldPiece, piece, edgePiece):
    if edgeBase == 4:
        angleBase = getArrete(pieceBase,edgeBase) & 1
        angleOldPiece = getArrete(oldPiece,edgeOldPiece) & 1
        anglePiece = getArrete(piece,edgePiece) & 1
        if angleBase + angleOldPiece + anglePiece != 1:
            return False
    return True


def bilan(cube):
    for piece in cube:
        print(bin(piece))


# Recursive function that aims to build the happy cube
def recursiveCube(cube,pieces,side):
    # Stop condition
    if len(pieces) == 1 or side >= 4:
        # Getting edges from last piece
        piece = pieces[0]

        # For each of those edges
        for numArrete in range(0,8):

            # If we did rotate for each of the sides, flip the piece to test every flipped sides
            if numArrete == 4:
                piece = flipPieceInPlace(piece)

            # Check compatibility between the last piece and every last edges
            if (checkEdgeCompatibility(getArrete(cube[1],1), getArrete(piece,1))
                and checkEdgeCompatibility(getArrete(cube[2],2), getArrete(piece,2))
                    and checkEdgeCompatibility(getArrete(cube[3],3), getArrete(piece,3))
                        and checkEdgeCompatibility(getArrete(cube[4],4), getArrete(piece,4))) :

                            # Hardcoding angles computation
                            angle1 = (getArrete(pieces[0],1) >> 4) + (getArrete(cube[3],4) >> 4) + (getArrete(cube[4],4) >> 4)
                            angle2 = (getArrete(pieces[0],2) >> 4) + (getArrete(cube[3],3) >> 4) + (getArrete(cube[2],3) >> 4)
                            angle3 = (getArrete(pieces[0],3) >> 4) + (getArrete(cube[1],2) >> 4) + (getArrete(cube[2],2) >> 4)
                            angle4 = (getArrete(pieces[0],4) >> 4) + (getArrete(cube[1],1) >> 4) + (getArrete(cube[4],1) >> 4)

                            # If each of those angles are validated, then it's 1+1+1+1 = 4
                            if angle1 + angle2 + angle3 + angle4 == 4:
                                cube.append(pieces[0])
                                #bilan(cube)
                                return True

            piece = rotatePiece(piece,1)
        return False

    else:
        # For each piece
        for piece in pieces :
            pieceOriginale = piece
            # For each rotation
            for i in range(0,8):
                # Here we do check for compatibility between the cube and the current piece
                # Looking at the compatibility between the current edge and the base's edge
                if checkEdgeCompatibility(getArrete(cube[0],side + 1), getArrete(piece,1)) :

                        # Now that the piece is able to be put on the base
                        # We do check several factors :
                        # 1-The compatibility between the new piece and the piece right before, since they have an edge in common
                        # 2-The compatibility in the angle formed by the base, the current piece and the piece right before
                        # 3,4 - Checking the same but for the next edge (Only happens when we are filling the last side of the base)
                        if side != 0 and (not checkEdgeCompatibility( getArrete(cube[-1],2 + side - 1),getArrete(piece,2))
                            or not checkAnglesCompatibility(
                                    getArrete(cube[0],side+1),
                                    getArrete(cube[-1],2 + side - 1),
                                    getArrete(piece,1)
                            )
                            or not checkFollowingEdgeCompatibility(cube[1],side+1, piece,4)
                            or not edgeBasecheckFollowingAnglesCompatibility(cube[0], side+1, cube[1],3,piece,4)) :

                            # Going to the next piece rotation before breaking to the next iteration
                            piece = rotatePiece(piece,1)
                            if i == 4:
                                piece = flipPieceInPlace(piece)

                            break

                        # Copying recursion vars to avoid their modification in the recursion
                        cubeCopy = cube.copy()
                        piecesCopy = pieces.copy()

                        # side + 2 % 4
                        # Generalising the number of rotation for the piece to be in the proper configuration with the base
                        # And adding the rotated piece to the cube
                        cubeCopy.append(rotatePiece(piece, (side + 2) % 4))

                        # Removing the just added piece of the list of available pieces
                        piecesCopy.remove(pieceOriginale)

                        # Now recurse
                        if recursiveCube(cubeCopy,piecesCopy,side+1) :
                            return True

                # Going to the next piece rotation before breaking to the next iteration
                piece = rotatePiece(piece,1)
                if i == 4:
                    piece = flipPieceInPlace(piece)
    return False

# Main function, which starts the recursions
def cube(pieces):
    for i in range(0,len(pieces)):
        cube = [pieces[i]]
        piecesCopy = pieces.copy()
        piecesCopy.remove(pieces[i])

        if recursiveCube(cube,piecesCopy,0):
            return True

    return False

lespieces = [
    # True
    [
        0b1101101001010010,
        0b0010110111010010,
        0b1101010101010010,
        0b1010010110100101,
        0b1101001000100010,
        0b0101001001010010,
    ],

    # True
    [
        0b1100110111010001,
        0b0010010100100110,
        0b0110011000100010,
        0b0010110111011100,
        0b0101001111000010,
        0b0101110001100010,
    ],

    # True
    [
        0b1101001001010101,
        0b1010010101010101,
        0b1101110101010010,
        0b1010110110101101,
        0b0010001000100010,
        0b0010001000100101,
    ],

    # False
    [
        0b1101001001010101,
        0b1010010101010101,
        0b1101110101110010,
        0b1010110110101101,
        0b0010001000100010,
        0b0010001000100101,
    ],

    # False
    [
        0b1101001001010101,
        0b1010010101010101,
        0b1101110101010010,
        0b1010110110101101,
        0b0010001000100010,
        0b0010001000100101,
    ]
]

for pieces in lespieces:
    print(cube(pieces))

#for i in range(0,100000):
#    print(cube([randint(0,2**16 - 1) for i in range(0,7)]))
