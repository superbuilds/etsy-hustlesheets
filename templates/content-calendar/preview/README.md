# Canvas preview harness
Renders a Sheets canvas component (App.jsx = code copied from the canvas's code view) with mock sheet data, for listing screenshots.
```
npm i react@18.3.1 react-dom@18.3.1 @dnd-kit/core@6.1.0 lucide-react@0.460.0 esbuild@0.24.0
curl -o tw.js https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.1.11/dist/index.global.js
npx esbuild main.jsx --bundle --outfile=bundle.js --jsx=automatic --define:process.env.NODE_ENV='"production"'
node shoot.js   # writes shots/*.png
```
Guide PDF: replace {{COPY_LINK}} in ../guide-template.html with the /copy link, then print to PDF.
