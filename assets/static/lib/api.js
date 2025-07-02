export const apiRequest = (url, method, data = null) => {
  const options = {
    credentials: "include",
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  return fetch(url, options);
};
