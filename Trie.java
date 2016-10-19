/*
Program to create a dictionary trie.
Each trie is a 27 way branch tree.
Positions 0-25 represent letters a-z (everything is lower case)
and position 26 is the null case for words that end
and still have words at levels below them.
For example, the word "he' is an entry, but the trie needs to
keep indexing wordsthat continue beyond the 2 letters "he"
such as "her" or "health" or "heat" etc.

Input is a text file of words that is supplied as the first
argument on the command line.  Output is just a listing of
the words in the trie in alphabetic order with their level
number printed out also.  Duplicate words in the input file
are flagged during insertion.

usage: java Trie filename

Restrictions: assumes nothing in the data file except alphabetical
characters (i.e. no digits, punctuation marks etc.)

*/

import java.io.*;

public class Trie   {

  public Trie[]  ltrie= new Trie[27];
  public  String[]  nodetype= new String[27];

// Constructor just creates a 27 way branch (with null pointers)
// for lower level tries (ltrie).
// A set of empty pointers (nodeptr) are used to hold words if needed
// at this level

  public Trie() {

  for(int i=0;i<27;i++){
      ltrie[i]=null;
      nodetype[i]=null;
  }
}

// trieInsert inserts a word into the dictionary trie.
// it checks for duplicates and ignores them

// s is the word being inserted and letpos is which letter
// we are at in the search

public void trieInsert(String s, int letpos)
{

int letter,nextletter;
// check to see if we are at end of word
   if (letpos+1>s.length()) letter=26;
     else letter=(int)(s.charAt(letpos) - 'a');//number between 0-25
   if(nodetype[letter]!=null) { // already inserted a word in this trie
      if(nodetype[letter].equals(s)){
        System.out.println("duplicate word inserted.." + s);
      } else { // need to create a new lower level trie
         String tmp = nodetype[letter]; // save this word
         ltrie[letter]=new Trie(); // link up new level trie
         nodetype[letter]=null; // cancel out the old pointer
// find out where the old word is inserted into lower level trie
         if(tmp.length() == (letpos+1))
             nextletter=26;
         else nextletter=(int)(tmp.charAt(letpos+1)-'a');
// now inseret the old word at the next level, and continue
// finding out where the new word goes
         ltrie[letter].nodetype[nextletter]=tmp;
         ltrie[letter].trieInsert(s,letpos+1);
      }
      return;
// this is the case where lower level tries already exist
    }
    if(ltrie[letter]!=null)
        ltrie[letter].trieInsert(s,letpos+1);
    else   // no lower levels, go insert new word in ths trie
        nodetype[letter]=s;
}
public void printTrie(int level)
{
  int i;
  if(nodetype[26]!=null)
     System.out.println("Trie word is " + nodetype[26] +
                      " at level " + level);
  for(i=0;i<26;i++)
    if(nodetype[i]!=null)
       System.out.println("Trie word is " + nodetype[i] +
                      " at level " + level);
    else if(ltrie[i]!=null)
            ltrie[i].printTrie(level+1);
}

public static void main(String[] args)
{

  try{
   String fileName=args[0]; //file of words name on command line
   File input= new File(fileName);
   StreamTokenizer tokenizer= new StreamTokenizer(
                 new BufferedReader(new FileReader(input)));
   tokenizer.lowerCaseMode(true);  // make it all lower case

   Trie T = new Trie(); // create top level trie

   while(tokenizer.nextToken()!=tokenizer.TT_EOF)  {
     if(tokenizer.ttype==tokenizer.TT_WORD) {
      String word=tokenizer.sval; // get the next word
      T.trieInsert(word,0);//insert it starting at letter position 0
     }
   }
   T.printTrie(0);
  }
  catch(IOException e)                 // Error reading in nextToken()
  {
      System.out.println(e);             // Output the error
      System.exit(1);                    // End the program
  }
}//end main
}// end Trie Class





