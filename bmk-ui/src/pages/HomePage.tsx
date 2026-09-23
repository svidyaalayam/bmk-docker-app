import { useEffect, useState } from "react";
import SiteHeader from "../components/SiteHeader";
import { useSchoolContent } from "../content/SchoolContentContext";
import {
  CLASS_SECTION_HEADERS,
  INTRODUCTION_HEADERS,
  scriptClassForLanguage,
} from "../types/content";
import type { Course, CourseClass, SecondaryLanguage } from "../types/content";

function splitParagraphs(text: string): string[] {
  return text
    .split(/\n\s*\n/)
    .map((part) => part.trim())
    .filter(Boolean);
}

function splitLines(text: string): string[] {
  return text
    .split(/\n+/)
    .map((part) => part.trim())
    .filter(Boolean);
}

function TextBlock({
  title,
  text,
  language,
}: {
  title: string;
  text: string;
  language?: SecondaryLanguage;
}) {
  if (!text.trim()) return null;
  const paragraphs = text.includes("\n\n")
    ? splitParagraphs(text)
    : splitLines(text);
  return (
    <div
      className={`class-detail-block ${language ? scriptClassForLanguage(language) : ""}`}
      lang={language || undefined}
    >
      <h5>{title}</h5>
      <ul className="class-detail-list">
        {paragraphs.map((paragraph) => (
          <li key={`${title}-${paragraph.slice(0, 40)}`}>{paragraph}</li>
        ))}
      </ul>
    </div>
  );
}

function useSecondaryDisplay(
  course: Course,
  schoolSecondaryLanguage: SecondaryLanguage,
): { useSecondary: boolean; language: SecondaryLanguage } {
  const configuredSecondary = Boolean(schoolSecondaryLanguage);
  const useSecondary =
    course.display_language === "secondary" && configuredSecondary;
  return {
    useSecondary,
    language: useSecondary ? schoolSecondaryLanguage : "",
  };
}

function ClassDetailPanel({
  courseClass,
  useSecondary,
  secondaryLanguage,
}: {
  courseClass: CourseClass;
  useSecondary: boolean;
  secondaryLanguage: SecondaryLanguage;
}) {
  const headers = useSecondary
    ? CLASS_SECTION_HEADERS[secondaryLanguage || ""]
    : CLASS_SECTION_HEADERS.en;

  const curriculum = useSecondary
    ? courseClass.curriculum_secondary
    : courseClass.curriculum;
  const aim = useSecondary ? courseClass.aim_secondary : courseClass.aim;
  const conditions = useSecondary
    ? courseClass.conditions_secondary
    : courseClass.conditions;

  return (
    <div className="class-detail-panel" role="tabpanel">
      <div className="class-detail-heading">
        <h4>{courseClass.name}</h4>
      </div>

      <TextBlock
        title={headers.curriculum}
        text={curriculum}
        language={useSecondary ? secondaryLanguage : undefined}
      />
      <TextBlock
        title={headers.aim}
        text={aim}
        language={useSecondary ? secondaryLanguage : undefined}
      />
      <TextBlock
        title={headers.conditions}
        text={conditions}
        language={useSecondary ? secondaryLanguage : undefined}
      />

    </div>
  );
}

function CourseBlock({
  course,
  schoolSecondaryLanguage,
}: {
  course: Course;
  schoolSecondaryLanguage: SecondaryLanguage;
}) {
  const [openClassId, setOpenClassId] = useState<number | null>(
    course.classes[0]?.id ?? null,
  );
  const { useSecondary, language } = useSecondaryDisplay(
    course,
    schoolSecondaryLanguage,
  );

  return (
    <article className="course-block">
      <div className="course-block-head">
        <div className="course-block-title-row">
          <h3>{course.title}</h3>
        </div>
        {course.display_language === "secondary" &&
          !schoolSecondaryLanguage && (
            <p className="muted-note">
              This course is set to secondary language, but School settings has
              no secondary language selected. Showing English for now.
            </p>
          )}
      </div>

      {course.classes.length === 0 ? (
        <p className="muted-note">No classes published for this course yet.</p>
      ) : (
        <div className="class-layout">
          <div
            className="class-tabs"
            role="tablist"
            aria-label={`${course.title} classes`}
          >
            {course.classes.map((courseClass) => {
              const selected = openClassId === courseClass.id;
              return (
                <button
                  key={courseClass.id}
                  type="button"
                  role="tab"
                  aria-selected={selected}
                  className={selected ? "class-tab active" : "class-tab"}
                  onClick={() => setOpenClassId(courseClass.id)}
                >
                  {courseClass.name}
                </button>
              );
            })}
          </div>

          {course.classes
            .filter((courseClass) => courseClass.id === openClassId)
            .map((courseClass) => (
              <ClassDetailPanel
                key={courseClass.id}
                courseClass={courseClass}
                useSecondary={useSecondary}
                secondaryLanguage={language}
              />
            ))}
        </div>
      )}
    </article>
  );
}

export default function HomePage() {
  const { loading, error, school, courses } = useSchoolContent();
  const secondaryLanguage = school.secondary_language;
  const showSecondary =
    Boolean(secondaryLanguage) && Boolean(school.introduction_secondary.trim());

  useEffect(() => {
    if (school.school_name) {
      document.title = school.school_name;
    }
  }, [school.school_name]);

  return (
    <div className="page-shell">
      <SiteHeader />

      <main>
        <section id="introduction" className="home-section first">
          {/* <div className="home-section-head">
            <div className="school-hero-brand">
              {school.logo_url && (
                <img
                  className="school-hero-logo"
                  src={school.logo_url}
                  alt={`${school.school_name} logo`}
                  width={56}
                  height={56}
                />
              )}
              <div>
                <h2>{school.school_name}</h2>
                <p>{school.tagline || 'About our school'}</p>
              </div>
            </div>
          </div> */}

          <div className={showSecondary ? "intro-bilingual" : undefined}>
            <article className="home-panel">
              <h3 className="intro-panel-title">{INTRODUCTION_HEADERS.en}</h3>
              {loading && <p>Loading school content…</p>}
              {error && <p className="error">{error}</p>}
              {!loading &&
                splitParagraphs(
                  school.introduction ||
                    "Introduction content will appear here once configured in Django admin.",
                ).map((paragraph) => (
                  <p key={paragraph.slice(0, 32)}>{paragraph}</p>
                ))}
            </article>

            {showSecondary && secondaryLanguage && (
              <article
                className={`home-panel intro-secondary ${scriptClassForLanguage(secondaryLanguage)}`}
                lang={secondaryLanguage}
              >
                <h3 className="intro-panel-title">
                  {INTRODUCTION_HEADERS[secondaryLanguage]}
                </h3>
                {splitParagraphs(school.introduction_secondary).map(
                  (paragraph) => (
                    <p key={paragraph.slice(0, 32)}>{paragraph}</p>
                  ),
                )}
              </article>
            )}
          </div>
        </section>

        <section id="courses" className="home-section">
          <div className="home-section-head">
            <h2>Courses & Classes</h2>
            <p>
              Each course has its own classes with aim, conditions, and
              curriculum
            </p>
          </div>

          {courses.length === 0 && !loading && (
            <article className="home-panel">
              <p>
                No courses published yet. Add courses and classes in Django
                admin.
              </p>
            </article>
          )}

          <div className="course-stack">
            {courses.map((course) => (
              <CourseBlock
                key={course.id}
                course={course}
                schoolSecondaryLanguage={secondaryLanguage}
              />
            ))}
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <p>{school.footer_text || school.school_name}</p>
      </footer>
    </div>
  );
}
