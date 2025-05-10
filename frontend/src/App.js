import React, { useState, useEffect } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    return saved === "true";
  });

  useEffect(() => {
    document.body.style.transition = "background-color 0.6s ease";
    document.body.style.backgroundColor = darkMode ? "#121212" : "#ffffff";
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      setResult({ answer: "Ошибка запроса", sources: [] });
    }

    setLoading(false);
  };

  const toggleTheme = () => setDarkMode(!darkMode);

  const backgroundColor = darkMode ? "#1e1e1e" : "#f5f5f5";
  const textColor = darkMode ? "#ffffff" : "#000000";
  const cardBg = darkMode ? "#2a2a2a" : "#ffffff";

  const skeletonStyle = {
    background: darkMode ? "#333" : "#ddd",
    borderRadius: "8px",
    width: "100%",
    height: "20px",
    animation: "pulse 1.5s infinite",
  };

  return (
    <div
      style={{
        maxWidth: "700px",
        margin: "2rem auto",
        fontFamily: "Arial, sans-serif",
        padding: "1rem",
        backgroundColor,
        color: textColor,
        transition: "background-color 0.6s ease, color 0.6s ease, box-shadow 0.6s ease",
        borderRadius: "12px",
      }}
    >
      {/* --- Header + Theme Toggle --- */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1 style={{ fontSize: "2rem" }}>WebRAG</h1>
        <div onClick={toggleTheme} style={{ cursor: "pointer", position: "relative", width: "60px", height: "30px" }}>
          <div
            style={{
              background: darkMode ? "#444" : "#ddd",
              borderRadius: "999px",
              width: "100%",
              height: "100%",
              position: "relative",
              transition: "background-color 0.6s ease",
            }}
          >
            <div
              style={{
                width: "22px",
                height: "22px",
                borderRadius: "50%",
                background: darkMode ? "#f9d71c" : "#333",
                color: darkMode ? "#000" : "#fff",
                fontSize: "14px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                position: "absolute",
                top: "4px",
                left: darkMode ? "34px" : "4px",
                transition: "left 0.3s ease, background-color 0.6s ease",
              }}
            >
              {darkMode ? "🌙" : "☀️"}
            </div>
          </div>
        </div>
      </div>

      {/* --- Form --- */}
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}>
        <input
          type="text"
          placeholder="Введите запрос..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            padding: "0.75rem",
            fontSize: "16px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            outline: "none",
            backgroundColor: darkMode ? "#333" : "#fff",
            color: darkMode ? "#fff" : "#000",
            transition: "background-color 0.6s ease, color 0.6s ease",
          }}
        />
        <button
          type="submit"
          style={{
            padding: "0.75rem 1.5rem",
            fontSize: "16px",
            backgroundColor: "#6c63ff",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
          }}
        >
          Отправить
        </button>
      </form>

      {/* --- Skeleton Loader --- */}
      {loading && (
        <div style={{ marginTop: "2rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ ...skeletonStyle, height: "22px", width: "30%" }} />
          <div style={skeletonStyle} />
          <div style={skeletonStyle} />
          <div style={{ ...skeletonStyle, width: "60%" }} />
        </div>
      )}

      {/* --- Result Block --- */}
      {result && (
        <div
          style={{
            marginTop: "2rem",
            backgroundColor: cardBg,
            padding: "1.5rem",
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
            transition: "background-color 0.6s ease",
          }}
        >
          <h2 style={{ marginBottom: "1rem" }}>Ответ:</h2>
          <p style={{ fontSize: "17px", lineHeight: "1.6", whiteSpace: "pre-line" }}>{result.answer}</p>

          {result.sources?.length > 0 && (
            <button
              onClick={() => setShowSources(true)}
              style={{
                marginTop: "1.5rem",
                padding: "0.5rem 1rem",
                backgroundColor: "#28a745",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
              }}
            >
              Показать источники
            </button>
          )}
        </div>
      )}

      {/* --- Sources Panel --- */}
      <div
        style={{
          position: "fixed",
          top: 0,
          right: showSources ? 0 : "-320px",
          width: "300px",
          height: "100vh",
          backgroundColor: cardBg,
          color: textColor,
          boxShadow: "-4px 0 12px rgba(0, 0, 0, 0.2)",
          padding: "1rem",
          transition: "right 0.3s ease, background-color 0.6s ease, color 0.6s ease",
          zIndex: 999,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3>Источники</h3>
          <button
            onClick={() => setShowSources(false)}
            style={{
              background: "transparent",
              border: "none",
              color: textColor,
              fontSize: "20px",
              cursor: "pointer",
            }}
          >
            ×
          </button>
        </div>

        <div style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {result?.sources?.map((url, idx) => (
            <a
              key={idx}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "block",
                padding: "0.5rem",
                backgroundColor: darkMode ? "#3a3a3a" : "#f0f0f0",
                color: darkMode ? "#9ddfff" : "#007bff",
                borderRadius: "6px",
                textDecoration: "none",
                fontSize: "14px",
                overflowWrap: "anywhere",
                transition: "background-color 0.6s ease, color 0.6s ease",
              }}
            >
              🔗 {new URL(url).hostname}
            </a>
          ))}
        </div>
      </div>

      {/* --- Skeleton Pulse Animation --- */}
      <style>
        {`
          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
          }
        `}
      </style>
    </div>
  );
}

export default App;
