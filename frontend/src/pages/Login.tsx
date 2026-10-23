import { Link, useNavigate } from "react-router-dom";
import { LoginForm, type LoginFormValues } from "@/components/auth/LoginForm";
import { login } from "@/services/auth-service";

/**
 * Login page: composes LoginForm (T033) + auth-service.login (T034).
 * On success the store is already updated (login() calls setUser), so
 * we just navigate to the dashboard.
 */
export default function Login() {
  const navigate = useNavigate();

  async function handleSubmit({ email, password }: LoginFormValues) {
    await login(email, password);
    navigate("/");
  }

  return (
    <div>
      <h1>로그인</h1>
      <LoginForm onSubmit={handleSubmit} />
      <p>
        계정이 없으신가요? <Link to="/register">회원가입</Link>
      </p>
    </div>
  );
}
