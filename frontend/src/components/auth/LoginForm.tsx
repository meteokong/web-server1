import { useId, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export interface LoginFormValues {
  email: string;
  password: string;
}

export interface LoginFormProps {
  /** Called with the entered credentials on submit. Reject to show an error. */
  onSubmit: (values: LoginFormValues) => Promise<void>;
}

/**
 * Presentational/interactive login form, mirroring RegisterForm's design:
 * it collects email/password and delegates to onSubmit, staying ignorant
 * of the auth API itself (that's auth-service's job, wired in by the
 * Login page, T036).
 */
export function LoginForm({ onSubmit }: LoginFormProps) {
  const emailId = useId();
  const passwordId = useId();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await onSubmit({ email, password });
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div>
        <label htmlFor={emailId}>이메일</label>
        <Input
          id={emailId}
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor={passwordId}>비밀번호</label>
        <Input
          id={passwordId}
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      {error && <p role="alert">{error}</p>}
      <Button type="submit" disabled={isSubmitting}>
        로그인
      </Button>
    </form>
  );
}
