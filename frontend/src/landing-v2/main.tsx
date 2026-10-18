import { lazy, StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "./globals.css";
import "./fonts.css";
import { AuthProvider, RequireAuth } from "../app/auth";

// each area is loaded on demand, so the landing animation code is not downloaded for the app screens
const Landing = lazy(() => import("./Landing"));
const Login = lazy(() => import("../app/Login"));
const AppLayout = lazy(() => import("../app/AppLayout"));
const Syllabuses = lazy(() => import("../app/Syllabuses"));
const Upload = lazy(() => import("../app/Upload"));
const Workspace = lazy(() => import("../app/Workspace"));

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={null}>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route
              path="/app"
              element={
                <RequireAuth>
                  <AppLayout />
                </RequireAuth>
              }
            >
              <Route index element={<Syllabuses />} />
              <Route path="new" element={<Upload />} />
              <Route path="s/:id" element={<Workspace />} />
            </Route>
            {/* any other address (for example the retired /landing.html) goes home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
