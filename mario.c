#include <stdio.h>
#include <cs50.h>

int main(void)
{
    // Prompt user for positive integer between 1 and 8
    int height, row, column, space;
    do
    {
        height = get_int("Height: ");
    }
    while (height > 8 || height < 1);

  //Print pyramid
    for (row = 0; row < height; row++)
    {
       for (space = 0; space < height - row - 1; space++)
       {
           printf(" ");
       }
       for (column = 0; column <= row; column++)
       {
           printf("#");
       }
       printf("\n");
    }
}