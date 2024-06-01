import React, {useState, useEffect} from 'react';
import './main.global.css';
import {Provider} from "react-redux";
import {createStore} from "redux";
import {BrowserRouter, Route, Navigate, Routes} from "react-router-dom";
import {rootReducer} from './store/reducer';
import {Header} from './components/Header';
import {EntryPage} from './components/EntryPage';
import {UploadingPage} from './components/UploadingPage';

const store = createStore(rootReducer);

function AppComponent() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <>
      {mounted &&
        <BrowserRouter>
          <Header />
          <Routes>
            <Route path="/" element={<EntryPage />} />
            <Route path="/load" element={<UploadingPage />} />
          </Routes>
        </BrowserRouter>
      }
    </>
  );
}

export const App = () => 
  <Provider store={store}>
    <AppComponent />
  </Provider>
;
