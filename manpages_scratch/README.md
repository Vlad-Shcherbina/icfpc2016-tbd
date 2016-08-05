File names
===

First number is problem size, second number is problem hash, third
number is problem id.

To get required field, you can use `cut`:

```
 ls -1 | grep problem | cut -d- -f3
```

to sort listings, use `sort`.
