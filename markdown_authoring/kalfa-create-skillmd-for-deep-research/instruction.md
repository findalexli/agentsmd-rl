# Create SKILL.md for Deep Research documentation

Source: [komunite/kalfa#17](https://github.com/komunite/kalfa/pull/17)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/academic-paper-reviewer/SKILL.md`
- `.claude/skills/deep-research/SKILL.md`

## What to add / change

Derin Araştırma Yeteneği Detaylı Dokümantasyonu
1. Kullanım Talimatları
Kullanıcı bir araştırma sorusu girdiğinde sistem şu adımları izler:

Sorgu Analizi: Araştırma sorusunun FINER (Feasible, Interesting, Novel, Ethical, Relevant) kriterlerine göre puanlanması.

Protokol Belirleme: Araştırma paradigmasının (Pragmatist, Pozitivist vb.) seçilmesi.

İteratif İlerleme: Her aşama tamamlandığında bir "Checkpoint" (Kontrol Noktası) onayı alınması.


2. İş Akışı (Workflow)
Scoping (Kapsam): Sınırların çizilmesi ve alt soruların oluşturulması.

Investigation (İnceleme): Kaynakçanın oluşturulması ve PRISMA akışı ile elemenin yapılması.

Analysis (Analiz): Kanıtların gücüne göre (Seviye I-VII) sınıflandırılması ve sentezlenmesi.

Composition (Yazım): Akademik formatta (APA, MLA) raporun derlenmesi.

Review & Revision (Gözden Geçirme): Editör ve Etik kontrolleri sonrası gerekli düzeltmelerin yapılması.

Test Edildi mi?
Senaryo 1: "YZ'nin yükseköğretim kalite güvencesine etkisi" konusu 22 kaynakla test edildi.

Senaryo 2: Kaynak doğrulama (Source Verification) ajanı, uydurma (halüsinasyon) kaynakları %95 başarıyla eledi.

Senaryo 3: Devil's Advocate kontrol noktası, rapordaki aşırı iyimser çıkarımları başarıyla tespit edip "hedging" (ihtiyatlı dil) uygulanmasını sağladı.

Checklist
[x] CLAUDE.md kurallarına uygun

[x] SKILL.md Türkçe çevirildi

Kaynak : https://github.com/Imbad0202/academic-research-skills

<!-- This is an auto-generated comment: release

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
