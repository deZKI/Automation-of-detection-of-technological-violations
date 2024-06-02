import React, {useState, useEffect} from 'react';
import './main.global.css';
import {Provider} from "react-redux";
import {BrowserRouter, Route, Navigate, Routes} from "react-router-dom";
import {composeWithDevTools} from "redux-devtools-extension";
import {applyMiddleware, createStore} from "redux";
import {rootReducer} from './store/reducer';
import {Header} from './components/Header';
import {EntryPage} from './components/EntryPage';
import {UploadingPage} from './components/UploadingPage';
import thunk from "redux-thunk";

const middleware = [thunk];
const store = createStore(rootReducer, composeWithDevTools(
  applyMiddleware(...middleware)
));

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
            <Route path="/load-panel" element={<UploadingPage />} />
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
