# Nanogram CSS compiler
--------------------------------------
## Cookbook:

- Edit sass files in /css/src/nanogram
- Edit /css/src/nanogram/nanogram.sass for selection inclusions
- Use sass to compile to css
- Minify css
- Copy css to /src for chip upload

Install Sass with:
```
sudo npm install -g sass
```

Convert to css:
```
sass ../src/nanogram/nanogram.sass nanogram.css
```

Minify:
```
cat nanogram.css| tr -d " \t\n\r" > nanogram.min.css
```


