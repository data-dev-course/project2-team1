import "dotenv/config";
import express from "express";
import morgan from "morgan";
import session from "express-session";
import flash from "express-flash";
import cors from "cors";
import path from "path";
import register from '@babel/register';

register({
  presets: ['@babel/preset-env']
});
const app = express();
const logger = morgan("dev");
const __dirname = path.resolve();
const PORT = process.env.PORT || 4000;

// SETUP
app.use(logger);
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(flash());
app.use(cors());
app.use("/uploads", express.static("uploads"));
app.use("/static", express.static("assets"));

const handleListening = () =>
  console.log(`✅ Server listenting on http://localhost:${PORT} 🚀`);

app.listen(PORT, handleListening);

app.use(express.static(path.join(__dirname, 'strayanimal/build')));
app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname, '/strayanimal/build/index.html'));
});
app.get('*', function (req, res) {
  res.sendFile(path.join(__dirname, '/strayanimal/build/index.html'));
});
