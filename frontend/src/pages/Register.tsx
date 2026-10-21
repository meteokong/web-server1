import { Link, useNavigate } from "react-router-dom";
import { RegisterForm, type RegisterFormValues } from "@/components/auth/RegisterForm";
import { register } from "@/services/auth-service";

/**
 * Register page: composes RegisterForm (T032) + auth-service.register
 * (T034). Per the auth-api contract, registering does NOT log the user
 * in (no cookies are set), so on success we send them to /login to sign
 * in with their new credentials, rather than straight to the dashboard.
 */
export default function Register() {
  const navigate = useNavigate();

  async function handleSubmit({ email, password }: RegisterFormValues) {
    await register(email, password);
    navigate("/login");
  }

  return (
    <div>
      <h1>회원가입</h1>
      <RegisterForm onSubmit={handleSubmit} />
      <p>
        이미 계정이 있으신가요? <Link to="/login">로그인</Link>
      </p>
    </div>
  );
}
