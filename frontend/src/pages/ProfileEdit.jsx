import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api";
import ErrorState from "../components/ErrorState";
import LoadingIndicator from "../components/ui/LoadingIndicator";
import { backendOrigin } from "../constants";

const resolveMediaUrl = (value) => {
  if (!value) return "";
  const str = String(value);
  if (str.startsWith("http://") || str.startsWith("https://")) return str;
  if (str.startsWith("/")) return `${backendOrigin}${str}`;
  return `${backendOrigin}/${str}`;
};

const ProfileEdit = () => {
  const { username } = useParams();
  const navigate = useNavigate();

  const viewerUsername = localStorage.getItem("username");
  const isOwnProfile = viewerUsername && username && viewerUsername === username;

  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    bio: "",
    phone_number: "",
    address: "",
    city: "",
    postal_code: "",
    country: "",
    marketing_emails: false,
    is_seller: false,
  });

  const [currentImage, setCurrentImage] = useState("");
  const [newImageFile, setNewImageFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!username) {
      setError("No username provided");
      setInitialLoading(false);
      return;
    }

    if (!isOwnProfile) {
      setError("You can only edit your own profile");
      setInitialLoading(false);
      return;
    }

    setError("");
    setInitialLoading(true);

    api
      .get(`/profile/${username}/`)
      .then((res) => {
        const p = res.data;
        setCurrentImage(p?.image || "");
        setForm({
          bio: p?.bio ?? "",
          phone_number: p?.phone_number ?? "",
          address: p?.address ?? "",
          city: p?.city ?? "",
          postal_code: p?.postal_code ?? "",
          country: p?.country ?? "",
          marketing_emails: Boolean(p?.marketing_emails),
          is_seller: Boolean(p?.is_seller),
        });
      })
      .catch(() => setError("Failed to load your profile"))
      .finally(() => setInitialLoading(false));
  }, [isOwnProfile, username]);

  const update = (name, value) => setForm((prev) => ({ ...prev, [name]: value }));

  const handleSubmit = useMemo(() => {
    return async (e) => {
      e.preventDefault();
      setError("");

      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v ?? ""));
      if (newImageFile) fd.append("image", newImageFile);

      try {
        setSubmitting(true);
        await api.patch(`/profile/${username}/edit/`, fd);
        navigate(`/profile/${username}`);
      } catch (err) {
        const data = err?.response?.data;
        if (typeof data === "string") setError(data);
        else if (data && typeof data === "object") {
          setError(
            Object.entries(data)
              .map(([field, msg]) => `${field}: ${Array.isArray(msg) ? msg.join(", ") : msg}`)
              .join("\n")
          );
        } else setError("Update failed");
      } finally {
        setSubmitting(false);
      }
    };
  }, [form, newImageFile, navigate, username]);

  if (error && initialLoading) return <LoadingIndicator />;
  if (error && !initialLoading) return <ErrorState title="Profile edit" message={error} />;
  if (initialLoading) return <LoadingIndicator />;

  return (
    <main className="screen-max-width px-8 py-24 flex justify-center">
      <form onSubmit={handleSubmit} className="form-container max-w-lg" encType="multipart/form-data">
        <h1 className="form-heading">Edit profile</h1>

        {error && <div className="mb-4 text-red-600 whitespace-pre-line">{error}</div>}

        {currentImage && (
          <img
            src={resolveMediaUrl(currentImage)}
            alt="Current avatar"
            className="w-32 h-32 rounded-full mb-4 border-2 border-black object-cover mx-auto"
          />
        )}

        <label className="label" htmlFor="image">Avatar</label>
        <input
          type="file"
          id="image"
          name="image"
          className="form-input"
          accept="image/*"
          onChange={(e) => setNewImageFile(e.target.files?.[0] ?? null)}
        />

        <label className="label" htmlFor="bio">Bio</label>
        <textarea
          id="bio"
          name="bio"
          className="form-input"
          value={form.bio}
          onChange={(e) => update(e.target.name, e.target.value)}
          rows={4}
        />

        <label className="label" htmlFor="phone_number">Phone</label>
        <input
          id="phone_number"
          name="phone_number"
          className="form-input"
          value={form.phone_number}
          onChange={(e) => update(e.target.name, e.target.value)}
        />

        <label className="label" htmlFor="address">Address</label>
        <input
          id="address"
          name="address"
          className="form-input"
          value={form.address}
          onChange={(e) => update(e.target.name, e.target.value)}
        />

        <label className="label" htmlFor="city">City</label>
        <input
          id="city"
          name="city"
          className="form-input"
          value={form.city}
          onChange={(e) => update(e.target.name, e.target.value)}
        />

        <label className="label" htmlFor="postal_code">Postal code</label>
        <input
          id="postal_code"
          name="postal_code"
          className="form-input"
          value={form.postal_code}
          onChange={(e) => update(e.target.name, e.target.value)}
        />

        <label className="label" htmlFor="country">Country</label>
        <input
          id="country"
          name="country"
          className="form-input"
          value={form.country}
          onChange={(e) => update(e.target.name, e.target.value)}
        />

        <label className="label flex items-center" htmlFor="is_seller">
          <input
            type="checkbox"
            id="is_seller"
            name="is_seller"
            checked={form.is_seller}
            onChange={(e) => update(e.target.name, e.target.checked)}
            className="mr-2"
          />
          <span>Seller account</span>
        </label>

        <label className="label flex items-center" htmlFor="marketing_emails">
          <input
            type="checkbox"
            id="marketing_emails"
            name="marketing_emails"
            checked={form.marketing_emails}
            onChange={(e) => update(e.target.name, e.target.checked)}
            className="mr-2"
          />
          <span>Marketing emails</span>
        </label>

        <button type="submit" className="form-btn" disabled={submitting}>
          {submitting ? "Saving..." : "Save changes"}
        </button>
      </form>
    </main>
  );
};

export default ProfileEdit;
