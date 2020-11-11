// include libraries
#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

// Start program
int main (void)
{
   char str[100];
   int length = 0, words = 1, i = 0, sent = 0, grade = 1;

        //Prompt user for a text
        string text = get_string("Text:");
        
        //Loop until the end of string
        while (text[i] != '\0')
        {
           //Count the number of letters except space
           if (text[i] != ' ')
           {
               length++;
           }
           //Check whether current character is a space, new line or tab
           else if (text[i] == ' ' || text[i] == '\n' || text[i] == '\t')
           {
               words++;
           }
           //Loop until end of sentence
           else if (text[i] == '.' || text[i] == '!' || text[i] == '?')
           {
              sent++;
           }
           i++;
        }
          //Print grade level using Coleman Liau index
          grade = round(0.0588 * 100*(length/words) - 0.296 * 100*(sent/words) - 15.8);

          //Check if grade is less than 1 or greater than 16
          if (grade < 1)
          {
              printf("Before Grade 1\n");
          }
          else if (grade >= 16)
          {
              printf("Grade 16+\n");
          }
          else
              printf("Grade %i\n", grade);
}
