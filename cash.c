#include <stdio.h>
#include <cs50.h>
#include <math.h>

int main(void)
{
    // Prompt user for a non-negative value
    float dollar;
      do
      {
         dollar = get_float("Change owed:");
      }
      while (dollar <= 0 );

    // Convert dollars to cents
    int cents, coins = 0;

        cents = round(dollar * 100);

    //Print the number of coins
    while (cents >= 25)
    {
       cents -= 25;
       coins++;
    }
    while (cents >= 10)
    {
      cents -= 10;
      coins++;
    }
    while (cents >= 5)
    {
      cents -= 5;
      coins++;
    }
    while (cents >= 1)
    {
      cents -= 1;
      coins++;
    }
       printf("%i\n", coins);
}