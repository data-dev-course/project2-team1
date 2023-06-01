import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import  { QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'
import reportWebVitals from './reportWebVitals';
import Intro from './components/Intro';
import { storageDataLoader } from './loaders/filedataLoader';

const queryClient = new QueryClient()
/** react-router-dom setting*/
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <div>Not Found</div>,
    loader: storageDataLoader,
    children: [
      { index: true, element: <Intro /> },
      {
        path: "protect-animal-list",
        element: <div>유기동물공고</div>,
      },
    ],
  },
  
]);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <QueryClientProvider client={queryClient}>
    <RouterProvider router={router} />
  </QueryClientProvider>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
