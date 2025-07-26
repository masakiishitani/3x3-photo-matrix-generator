from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
from typing import List, Dict, Tuple
import os
import glob
import sys

class PhotoMatrixGenerator:
    """
    写真マトリクス生成システムのメインクラス
    """
    
    def __init__(self):
        # MakeShop仕様
        self.canvas_size = (2520, 2520)
        self.dpi = 200
        self.output_format = 'PNG'
        
        # レイアウトパターン
        self.layouts = {
            'portrait': {'cell_size': (680, 1020), 'spacing': 60},
            'landscape': {'cell_size': (840, 560), 'spacing': 0},
            'square': {'cell_size': (840, 840), 'spacing': 0}
        }
    
    def generate_matrix(self, photo_paths: List[str], output_path: str) -> str:
        """
        写真パスリストからマトリクスを生成
        
        Args:
            photo_paths: 写真ファイルパスのリスト
            output_path: 出力ファイルパス
        
        Returns:
            生成された画像ファイルパス
        """
        # 写真読み込み・検証
        photos = self._load_and_validate_photos(photo_paths)
        
        if not photos:
            raise ValueError("有効な写真が見つかりません")
        
        # 写真数に応じた処理
        if len(photos) == 9:
            processed_photos = photos
        elif len(photos) < 9:
            processed_photos = self._supplement_photos(photos)
        else:
            processed_photos = photos[:9]  # 最初の9枚を使用
        
        # レイアウト決定
        layout_type = self._determine_layout(processed_photos)
        
        # 配置最適化
        placement = self._optimize_placement(processed_photos)
        
        # マトリクス生成
        matrix_image = self._create_matrix(processed_photos, placement, layout_type)
        
        # MakeShop仕様で保存
        self._save_makeshop_format(matrix_image, output_path)
        
        return output_path
    
    def _load_and_validate_photos(self, photo_paths: List[str]) -> List[Image.Image]:
        """写真の読み込みと検証"""
        photos = []
        for path in photo_paths:
            try:
                img = Image.open(path)
                print(f"画像情報: {os.path.basename(path)} - サイズ: {img.size}, フォーマット: {img.format}, モード: {img.mode}")
                
                if self._validate_photo(img):
                    # RGB変換
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    photos.append(img)
                    print(f"読み込み成功: {os.path.basename(path)}")
                else:
                    print(f"検証失敗: {os.path.basename(path)}")
            except Exception as e:
                print(f"写真読み込みエラー: {path} - {e}")
        return photos
    
    def _validate_photo(self, img: Image.Image) -> bool:
        """写真の有効性チェック"""
        # 最小サイズチェック
        if img.size[0] < 300 or img.size[1] < 300:
            print(f"サイズが小さすぎます: {img.size}")
            return False
        # ファイル形式チェック（WEBPも追加）
        if img.format not in ['JPEG', 'PNG', 'WEBP']:
            print(f"対応していないフォーマット: {img.format}")
            return False
        return True
    
    def _determine_layout(self, photos: List[Image.Image]) -> str:
        """最適レイアウトの決定"""
        aspect_ratios = [img.size[0] / img.size[1] for img in photos]
        avg_ratio = np.mean(aspect_ratios)
        
        print(f"平均アスペクト比: {avg_ratio:.2f}")
        
        if avg_ratio > 1.3:
            layout = 'landscape'
        elif avg_ratio < 0.8:
            layout = 'portrait'
        else:
            layout = 'square'
        
        print(f"選択されたレイアウト: {layout}")
        return layout
    
    def _optimize_placement(self, photos: List[Image.Image]) -> Dict[int, int]:
        """3×3グリッド最適配置"""
        # 写真品質スコア計算
        scores = []
        for i, photo in enumerate(photos):
            score = self._calculate_photo_score(photo)
            scores.append((i, score))
            print(f"写真{i+1} スコア: {score:.3f}")
        
        # スコア順ソート
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 配置決定
        placement = {}
        placement[3] = scores[0][0]  # フォーカルポイント（右上）
        placement[1] = scores[1][0]  # エントランス（左上）
        placement[2] = scores[2][0]  # ブリッジ（上中央）
        
        # 残りの配置
        remaining_positions = [4, 5, 6, 7, 8, 9]
        for i, pos in enumerate(remaining_positions):
            if i + 3 < len(scores):
                placement[pos] = scores[i + 3][0]
        
        print("配置最適化結果:")
        for pos, photo_idx in placement.items():
            print(f"  位置{pos}: 写真{photo_idx+1}")
        
        return placement
    
    def _calculate_photo_score(self, photo: Image.Image) -> float:
        """写真品質スコア計算"""
        # 解像度スコア
        resolution_score = min(photo.size[0] * photo.size[1] / (1920 * 1080), 1.0)
        
        # アスペクト比スコア
        aspect_ratio = photo.size[0] / photo.size[1]
        aspect_score = 1.0 - abs(1.0 - aspect_ratio) * 0.5
        
        # 色彩豊かさスコア
        color_score = self._calculate_color_richness(photo)
        
        return resolution_score * 0.3 + aspect_score * 0.3 + color_score * 0.4
    
    def _calculate_color_richness(self, photo: Image.Image) -> float:
        """色彩豊かさ計算"""
        # 小さくリサイズして処理高速化
        small = photo.resize((100, 100))
        pixels = np.array(small)
        
        # 色の分散計算
        color_variance = np.var(pixels, axis=(0, 1))
        avg_variance = np.mean(color_variance)
        
        return min(avg_variance / 10000, 1.0)
    
    def _supplement_photos(self, photos: List[Image.Image]) -> List[Image.Image]:
        """9枚未満の写真を背景で補完"""
        supplemented = photos.copy()
        needed = 9 - len(photos)
        
        print(f"{needed}枚の背景を生成します")
        
        # 主要色抽出
        colors = self._extract_dominant_colors(photos)
        
        # 背景生成
        for i in range(needed):
            bg = self._generate_background(colors, i)
            supplemented.append(bg)
        
        return supplemented
    
    def _extract_dominant_colors(self, photos: List[Image.Image]) -> List[Tuple[int, int, int]]:
        """主要色抽出"""
        all_colors = []
        for photo in photos:
            small = photo.resize((50, 50))
            pixels = np.array(small).reshape(-1, 3)
            
            # 簡単な色抽出（K-meansの代わり）
            mean_color = np.mean(pixels, axis=0).astype(int)
            all_colors.append(tuple(mean_color))
        
        return all_colors
    
    def _generate_background(self, colors: List[Tuple[int, int, int]], index: int) -> Image.Image:
        """調和背景生成"""
        size = (800, 800)
        bg = Image.new('RGB', size)
        draw = ImageDraw.Draw(bg)
        
        # 色選択
        if colors:
            base_color = colors[index % len(colors)]
            # 色を薄くして控えめに
            base_color = tuple(min(255, int(c * 1.2 + 50)) for c in base_color)
        else:
            base_color = (245, 245, 245)
        
        # シンプルな単色背景
        draw.rectangle([0, 0, size[0], size[1]], fill=base_color)
        
        # 微細なテクスチャ追加
        for i in range(0, size[0], 20):
            for j in range(0, size[1], 20):
                if (i + j) % 40 == 0:
                    noise_color = tuple(max(0, min(255, c + (-5 if (i + j) % 80 == 0 else 5))) for c in base_color)
                    draw.rectangle([i, j, i+10, j+10], fill=noise_color)
        
        return bg
    
    def _create_matrix(self, photos: List[Image.Image], placement: Dict[int, int], 
                      layout_type: str) -> Image.Image:
        """マトリクス画像生成"""
        # キャンバス作成（透過背景）
        canvas = Image.new('RGBA', self.canvas_size, (255, 255, 255, 0))
        
        # レイアウト設定
        layout = self.layouts[layout_type]
        cell_size = layout['cell_size']
        spacing = layout['spacing']
        
        print(f"キャンバスサイズ: {self.canvas_size}")
        print(f"セルサイズ: {cell_size}, 間隔: {spacing}")
        
        # 写真配置
        for position in range(1, 10):
            if position in placement:
                photo_idx = placement[position]
                photo = photos[photo_idx]
                
                # グリッド座標計算
                row = (position - 1) // 3
                col = (position - 1) % 3
                
                # 配置座標
                x = col * (cell_size[0] + spacing)
                y = row * (cell_size[1] + spacing)
                
                # 写真リサイズ・配置
                resized = self._resize_for_cell(photo, cell_size)
                canvas.paste(resized, (x, y))
                
                print(f"位置{position}: ({x}, {y}) に配置")
        
        # 最終調整
        return self._enhance_image(canvas)
    
    def _resize_for_cell(self, photo: Image.Image, cell_size: Tuple[int, int]) -> Image.Image:
        """セル用リサイズ"""
        # アスペクト比保持リサイズ
        photo_ratio = photo.size[0] / photo.size[1]
        cell_ratio = cell_size[0] / cell_size[1]
        
        if photo_ratio > cell_ratio:
            new_height = cell_size[1]
            new_width = int(new_height * photo_ratio)
        else:
            new_width = cell_size[0]
            new_height = int(new_width / photo_ratio)
        
        resized = photo.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 中央クロップ
        if resized.size != cell_size:
            result = Image.new('RGBA', cell_size, (255, 255, 255, 0))
            paste_x = (cell_size[0] - resized.size[0]) // 2
            paste_y = (cell_size[1] - resized.size[1]) // 2
            
            if paste_x >= 0 and paste_y >= 0:
                result.paste(resized, (paste_x, paste_y))
            else:
                crop_x = max(0, -paste_x)
                crop_y = max(0, -paste_y)
                crop_w = min(resized.size[0], cell_size[0])
                crop_h = min(resized.size[1], cell_size[1])
                
                cropped = resized.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
                result.paste(cropped, (max(0, paste_x), max(0, paste_y)))
            
            return result
        
        return resized
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """画像品質向上"""
        # シャープネス
        sharpened = image.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=3))
        
        # 色彩強化
        color_enhancer = ImageEnhance.Color(sharpened)
        color_enhanced = color_enhancer.enhance(1.05)
        
        return color_enhanced
    
    def _save_makeshop_format(self, image: Image.Image, output_path: str):
        """MakeShop仕様保存"""
        # DPI設定
        image.info['dpi'] = (self.dpi, self.dpi)
        
        # PNG保存
        image.save(output_path, format=self.output_format, dpi=(self.dpi, self.dpi))
        print(f"保存完了: {output_path}")


class BatchMatrixGenerator:
    """複数マトリクス生成対応"""
    
    def __init__(self):
        self.generator = PhotoMatrixGenerator()
    
    def process_multiple_photos(self, photo_paths: List[str], output_dir: str) -> List[str]:
        """9枚以上の写真を複数マトリクスに分割処理"""
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        matrix_count = 0
        
        print(f"総写真数: {len(photo_paths)}枚")
        print(f"予想マトリクス数: {(len(photo_paths) + 8) // 9}個")
        
        # 9枚ずつ処理
        for i in range(0, len(photo_paths), 9):
            batch = photo_paths[i:i+9]
            matrix_count += 1
            
            print(f"\nマトリクス{matrix_count}: {len(batch)}枚の写真を使用")
            for j, path in enumerate(batch):
                print(f"  {j+1}. {os.path.basename(path)}")
            
            output_path = os.path.join(output_dir, f"matrix_{matrix_count:03d}.png")
            
            try:
                result_path = self.generator.generate_matrix(batch, output_path)
                generated_files.append(result_path)
                print(f"マトリクス{matrix_count}生成完了")
            except Exception as e:
                print(f"マトリクス{matrix_count}生成エラー: {e}")
        
        return generated_files


def main():
    if len(sys.argv) < 3:
        print("使用方法: python matrix_generator.py <写真ディレクトリ> <出力ファイルまたはディレクトリ>")
        return
    
    input_dir = sys.argv[1]
    output_path = sys.argv[2]
    
    # ディレクトリ存在確認
    if not os.path.exists(input_dir):
        print(f"エラー: 入力ディレクトリが見つかりません: {input_dir}")
        return
    
    # 写真ファイル検索
    photo_patterns = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    photo_paths = []
    
    for pattern in photo_patterns:
        photo_paths.extend(glob.glob(os.path.join(input_dir, pattern)))
    
    if not photo_paths:
        print(f"エラー: 写真ファイルが見つかりません: {input_dir}")
        return
    
    print(f"発見された写真: {len(photo_paths)}枚")
    
    # マトリクス生成
    if len(photo_paths) <= 9:
        # 単一マトリクス
        generator = PhotoMatrixGenerator()
        result = generator.generate_matrix(photo_paths, output_path)
        print(f"マトリクス生成完了: {result}")
    else:
        # 複数マトリクス
        batch_generator = BatchMatrixGenerator()
        output_dir = output_path if os.path.isdir(output_path) else os.path.dirname(output_path)
        results = batch_generator.process_multiple_photos(photo_paths, output_dir)
        print(f"複数マトリクス生成完了: {len(results)}個")
        for result in results:
            print(f"  {result}")


if __name__ == "__main__":
    main()

