void main() {
    int n;        /* The number of fibonacci numbers we will print */
    int i;        /* The index of fibonacci number to be printed next */ 
    int current;  /* The value of the (i)th fibonacci number */
    int next;     /* The value of the (i+1)th fibonacci number */
    int twoaway;  /* The value of the (i+2)th fibonacci number */

    putString("How many Fibonacci numbers do you want to compute? ");
    n = getInt();
    if (n<=0)
       putString("The number should be positive.\n");
    else {
      putString("\n\n\tI \t Fibonacci(I) \n\t=====================\n");
      next = current = 1;
      for (i=1; i<=n; i=i+1) {
	putString("\t");
        putInt(i);
	putString("\t");
  	putIntLn(current);
	twoaway = current+next;
	current = next;
	next    = twoaway;
      }
    }
}